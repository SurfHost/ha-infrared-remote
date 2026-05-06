"""NEC IR protocol encoder and friends.

Provides standalone implementations that produce raw timing data compatible
with the Home Assistant InfraredCommand interface. We don't depend on the
infrared-protocols library (it may not have what we need or may not be
installed).

NEC protocol:
  - Carrier: 38 kHz
  - Unit: 560 us
  - Header: 9000us mark, 4500us space
  - Bit 1: 560us mark, 1690us space
  - Bit 0: 560us mark, 560us space
  - Data: 32 bits LSB first
    - 8-bit address + 8-bit inverted address + 8-bit command + 8-bit inverted command
  - Stop bit: 560us mark
  - Total frame time: ~67.5ms
"""

from __future__ import annotations

from .broadlink_decode import Timing, decode_broadlink_b64_to_timings
from .const import (
    NEC_FREQUENCY_KHZ,
    NEC_HEADER_MARK_US,
    NEC_HEADER_SPACE_US,
    NEC_ONE_MARK_US,
    NEC_ONE_SPACE_US,
    NEC_STOP_MARK_US,
    NEC_STOP_SPACE_US,
    NEC_ZERO_MARK_US,
    NEC_ZERO_SPACE_US,
)


class NECCommand:
    """NEC protocol IR command that provides raw timings.

    Implements the same interface as InfraredCommand:
    - modulation: carrier frequency in kHz
    - repeat_count: number of times to repeat
    - get_raw_timings(): returns list of Timing objects
    """

    def __init__(
        self,
        address: int,
        command: int,
        repeat_count: int = 0,
    ) -> None:
        """Initialize NEC command.

        Args:
            address: 8-bit device address (0x00-0xFF)
            command: 8-bit command code (0x00-0xFF)
            repeat_count: number of additional times to transmit
        """
        self.address = address & 0xFF
        self.command = command & 0xFF
        self.repeat_count = repeat_count
        self.modulation = NEC_FREQUENCY_KHZ

    def _encode_byte_lsb(self, byte: int) -> list[Timing]:
        """Encode a single byte as NEC timings, LSB first."""
        timings = []
        for bit_idx in range(8):
            bit = (byte >> bit_idx) & 1
            if bit:
                timings.append(Timing(high_us=NEC_ONE_MARK_US, low_us=NEC_ONE_SPACE_US))
            else:
                timings.append(Timing(high_us=NEC_ZERO_MARK_US, low_us=NEC_ZERO_SPACE_US))
        return timings

    def get_raw_timings(self) -> list[Timing]:
        """Get the complete NEC frame as raw mark/space timings."""
        timings: list[Timing] = []

        timings.append(Timing(high_us=NEC_HEADER_MARK_US, low_us=NEC_HEADER_SPACE_US))
        timings.extend(self._encode_byte_lsb(self.address))
        timings.extend(self._encode_byte_lsb(~self.address & 0xFF))
        timings.extend(self._encode_byte_lsb(self.command))
        timings.extend(self._encode_byte_lsb(~self.command & 0xFF))
        timings.append(Timing(high_us=NEC_STOP_MARK_US, low_us=NEC_STOP_SPACE_US))

        return timings


class RawBroadlinkCommand:
    """IR command decoded from a Broadlink-learned base64 packet.

    Used for protocols we can't easily encode from scratch (e.g., RC6).
    """

    def __init__(self, b64_code: str, repeat_count: int = 0) -> None:
        """Initialize from a Broadlink base64-encoded IR packet."""
        self.repeat_count = repeat_count
        self.modulation = NEC_FREQUENCY_KHZ  # 38 kHz default
        self._timings = decode_broadlink_b64_to_timings(b64_code)

    def get_raw_timings(self) -> list[Timing]:
        """Get the decoded raw timings."""
        return self._timings


class RawTestCommand:
    """A simple raw test signal for verifying the IR chain works."""

    def __init__(self, repeat_count: int = 0) -> None:
        """Initialize raw test command."""
        self.repeat_count = repeat_count
        self.modulation = NEC_FREQUENCY_KHZ  # 38 kHz

    def get_raw_timings(self) -> list[Timing]:
        """Get a simple test pattern as raw timings."""
        timings: list[Timing] = []
        timings.append(Timing(high_us=9000, low_us=4500))
        for _ in range(8):
            timings.append(Timing(high_us=560, low_us=1690))
        for _ in range(8):
            timings.append(Timing(high_us=560, low_us=560))
        timings.append(Timing(high_us=560, low_us=560))
        return timings
