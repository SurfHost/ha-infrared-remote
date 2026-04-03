"""NEC IR protocol encoder for the IR Test Remote.

This module provides a standalone NEC encoder that produces raw timing data
compatible with the Home Assistant InfraredCommand interface. This way we
don't depend on the infrared-protocols library (which may not be installed
yet or may have a different API).

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

For this test integration, we implement InfraredCommand ourselves using
raw timings so it works even if the infrared-protocols library doesn't
have what we need.
"""

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass
class Timing:
    """A single mark/space timing pair."""

    high_us: int  # Mark (IR on) duration in microseconds
    low_us: int  # Space (IR off) duration in microseconds


class NECCommand:
    """NEC protocol IR command that provides raw timings.

    This class implements the same interface as InfraredCommand:
    - modulation: carrier frequency in kHz
    - repeat_count: number of times to repeat
    - get_raw_timings(): returns list of Timing objects

    It encodes an 8-bit address and 8-bit command into the standard
    NEC 32-bit frame format.
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
        """Get the complete NEC frame as raw mark/space timings.

        Frame structure:
          [header] [address] [~address] [command] [~command] [stop]
        """
        timings: list[Timing] = []

        # Header burst
        timings.append(
            Timing(high_us=NEC_HEADER_MARK_US, low_us=NEC_HEADER_SPACE_US)
        )

        # Address byte (LSB first)
        timings.extend(self._encode_byte_lsb(self.address))

        # Inverted address byte
        timings.extend(self._encode_byte_lsb(~self.address & 0xFF))

        # Command byte (LSB first)
        timings.extend(self._encode_byte_lsb(self.command))

        # Inverted command byte
        timings.extend(self._encode_byte_lsb(~self.command & 0xFF))

        # Stop bit
        timings.append(
            Timing(high_us=NEC_STOP_MARK_US, low_us=NEC_STOP_SPACE_US)
        )

        return timings


class RawBroadlinkCommand:
    """IR command decoded from a Broadlink-learned base64 packet.

    Used for protocols we can't easily encode from scratch (e.g., RC6).
    Decodes the raw timing data from the Broadlink packet format and
    provides it as Timing objects compatible with InfraredCommand.
    """

    def __init__(self, b64_code: str, repeat_count: int = 0) -> None:
        """Initialize from a Broadlink base64-encoded IR packet."""
        import base64
        import struct

        self.repeat_count = repeat_count
        self.modulation = NEC_FREQUENCY_KHZ  # 38 kHz default

        data = base64.b64decode(b64_code)
        length = struct.unpack("<H", data[2:4])[0]
        timing_data = data[4 : 4 + length]

        # Broadlink tick = 269/8192 seconds ≈ 32.84µs
        tick_us = 269000 / 8192

        raw_us: list[int] = []
        i = 0
        while i < len(timing_data):
            if timing_data[i] == 0x00 and i + 2 < len(timing_data):
                val = (timing_data[i + 1] << 8) | timing_data[i + 2]
                i += 3
            else:
                val = timing_data[i]
                i += 1
            raw_us.append(round(val * tick_us))

        # Convert to mark/space Timing pairs (skip inter-frame gaps > 50ms)
        self._timings: list[Timing] = []
        idx = 0
        while idx + 1 < len(raw_us):
            mark = raw_us[idx]
            space = raw_us[idx + 1]
            if space > 50000:
                # End of first frame — skip repeat frames
                self._timings.append(Timing(high_us=mark, low_us=mark))
                break
            self._timings.append(Timing(high_us=mark, low_us=space))
            idx += 2

    def get_raw_timings(self) -> list[Timing]:
        """Get the decoded raw timings."""
        return self._timings


class RawTestCommand:
    """A simple raw test signal for verifying the IR chain works.

    Sends a distinctive pattern: a long burst followed by alternating
    short on/off pulses. If your Broadlink RM4 Pro's LED blinks when
    you trigger this, you know the whole chain works.
    """

    def __init__(self, repeat_count: int = 0) -> None:
        """Initialize raw test command."""
        self.repeat_count = repeat_count
        self.modulation = NEC_FREQUENCY_KHZ  # 38 kHz

    def get_raw_timings(self) -> list[Timing]:
        """Get a simple test pattern as raw timings."""
        timings: list[Timing] = []

        # Long initial burst (easily visible on scope / IR detector)
        timings.append(Timing(high_us=9000, low_us=4500))

        # 8 alternating pulses
        for _ in range(8):
            timings.append(Timing(high_us=560, low_us=1690))

        # 8 more with different pattern
        for _ in range(8):
            timings.append(Timing(high_us=560, low_us=560))

        # End burst
        timings.append(Timing(high_us=560, low_us=560))

        return timings
