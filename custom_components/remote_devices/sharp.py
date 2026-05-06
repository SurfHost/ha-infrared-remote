"""Sharp and Denon IR protocol encoders.

Despite being in the same protocol family, Sharp and Denon use different
timing values and slightly different frame structures. This module
provides separate encoders for each.

Sharp protocol:
  - Carrier: 38 kHz
  - No header pulse
  - Bit mark: 320us
  - Bit 1: 320us mark, 1680us space
  - Bit 0: 320us mark, 680us space
  - Data: 5-bit address + 8-bit command + 1 expansion + 1 check (LSB first)
  - Two frames: first normal, 40ms gap, second with inverted cmd/exp/chk

Denon protocol:
  - Carrier: 38 kHz
  - No header pulse (data starts immediately)
  - Time unit: 264us
  - Bit mark: 264us (1 unit)
  - Bit 1: 264us mark, 1848us space (7 units)
  - Bit 0: 264us mark, 792us space (3 units)
  - Data: 5-bit address + 8-bit command + 2-bit extension (LSB first)
  - Two frames: first with ext=0, second with inverted cmd and ext=3
  - Frame gap: 43560us (165 units)
"""

from __future__ import annotations

from .const import (
    DENON_BIT_MARK_US,
    DENON_FRAME_GAP_US,
    DENON_FREQUENCY_KHZ,
    DENON_ONE_SPACE_US,
    DENON_ZERO_SPACE_US,
    SHARP_BIT_MARK_US,
    SHARP_FRAME_GAP_US,
    SHARP_FREQUENCY_KHZ,
    SHARP_ONE_SPACE_US,
    SHARP_ZERO_SPACE_US,
)
from .broadlink_decode import Timing


class SharpCommand:
    """Sharp protocol IR command that provides raw timings.

    Implements the same interface as NECCommand / InfraredCommand.
    Encodes a 5-bit address and 8-bit command into the Sharp two-frame format.
    """

    def __init__(
        self,
        address: int,
        command: int,
        expansion: int = 1,
        check: int = 0,
        repeat_count: int = 0,
    ) -> None:
        """Initialize Sharp command.

        Args:
            address: 5-bit device address (0x00-0x1F)
            command: 8-bit command code (0x00-0xFF)
            expansion: expansion bit (typically 1)
            check: check bit (typically 0)
            repeat_count: number of additional times to transmit
        """
        self.address = address & 0x1F
        self.command = command & 0xFF
        self.expansion = expansion & 0x01
        self.check = check & 0x01
        self.repeat_count = repeat_count
        self.modulation = SHARP_FREQUENCY_KHZ

    def _encode_bits_lsb(self, value: int, num_bits: int) -> list[Timing]:
        """Encode bits as Sharp timings, LSB first."""
        timings = []
        for bit_idx in range(num_bits):
            bit = (value >> bit_idx) & 1
            if bit:
                timings.append(
                    Timing(high_us=SHARP_BIT_MARK_US, low_us=SHARP_ONE_SPACE_US)
                )
            else:
                timings.append(
                    Timing(high_us=SHARP_BIT_MARK_US, low_us=SHARP_ZERO_SPACE_US)
                )
        return timings

    def _encode_frame(self, invert: bool = False) -> list[Timing]:
        """Encode a single Sharp frame (15 bits + stop)."""
        timings: list[Timing] = []

        # Address: 5 bits (same in both frames)
        timings.extend(self._encode_bits_lsb(self.address, 5))

        # Command: 8 bits (inverted in second frame)
        cmd = (~self.command & 0xFF) if invert else self.command
        timings.extend(self._encode_bits_lsb(cmd, 8))

        # Expansion bit (inverted in second frame)
        exp = (self.expansion ^ 1) if invert else self.expansion
        timings.extend(self._encode_bits_lsb(exp, 1))

        # Check bit (inverted in second frame)
        chk = (self.check ^ 1) if invert else self.check
        timings.extend(self._encode_bits_lsb(chk, 1))

        # Stop bit
        timings.append(Timing(high_us=SHARP_BIT_MARK_US, low_us=SHARP_ZERO_SPACE_US))

        return timings

    def get_raw_timings(self) -> list[Timing]:
        """Get the complete Sharp two-frame sequence as raw timings."""
        timings: list[Timing] = []

        # First frame (normal)
        timings.extend(self._encode_frame(invert=False))

        # Replace the last timing's space with the inter-frame gap
        if timings:
            last = timings[-1]
            timings[-1] = Timing(high_us=last.high_us, low_us=SHARP_FRAME_GAP_US)

        # Second frame (inverted command/expansion/check)
        timings.extend(self._encode_frame(invert=True))

        return timings


class DenonCommand:
    """Denon protocol IR command that provides raw timings.

    Denon uses different timing from Sharp (264us base unit vs 320us)
    and has NO header pulse. Data starts immediately with address bits.
    Uses 2 extension bits instead of Sharp's expansion + check bits.

    IRP: {38k,264}<1,-3|1,-7>(D:5,F:8,0:2,1,-165,D:5,~F:8,3:2,1,-165)+

    Frame: 5-bit address + 8-bit command + 2-bit extension (no header)
    Two frames: first with ext=0, second with inverted cmd and ext=3.
    """

    def __init__(
        self,
        address: int,
        command: int,
        repeat_count: int = 0,
    ) -> None:
        """Initialize Denon command.

        Args:
            address: 5-bit device address (0x00-0x1F)
            command: 8-bit command code (0x00-0xFF)
            repeat_count: number of additional times to transmit
        """
        self.address = address & 0x1F
        self.command = command & 0xFF
        self.repeat_count = repeat_count
        self.modulation = DENON_FREQUENCY_KHZ

    def _encode_bits_lsb(self, value: int, num_bits: int) -> list[Timing]:
        """Encode bits as Denon timings, LSB first."""
        timings = []
        for bit_idx in range(num_bits):
            bit = (value >> bit_idx) & 1
            if bit:
                timings.append(
                    Timing(high_us=DENON_BIT_MARK_US, low_us=DENON_ONE_SPACE_US)
                )
            else:
                timings.append(
                    Timing(high_us=DENON_BIT_MARK_US, low_us=DENON_ZERO_SPACE_US)
                )
        return timings

    def _encode_frame(
        self, command: int, extension: int
    ) -> list[Timing]:
        """Encode a single Denon frame: 15 data bits + stop (no header)."""
        timings: list[Timing] = []

        # Address: 5 bits
        timings.extend(self._encode_bits_lsb(self.address, 5))

        # Command: 8 bits
        timings.extend(self._encode_bits_lsb(command, 8))

        # Extension: 2 bits
        timings.extend(self._encode_bits_lsb(extension, 2))

        # Stop bit
        timings.append(
            Timing(high_us=DENON_BIT_MARK_US, low_us=DENON_ZERO_SPACE_US)
        )

        return timings

    def get_raw_timings(self) -> list[Timing]:
        """Get the complete Denon two-frame sequence as raw timings.

        Frame 1: address + command + ext=0 + stop
        Gap: 43.5ms
        Frame 2: address + ~command + ext=3 + stop
        """
        timings: list[Timing] = []

        # First frame: normal command, extension = 0
        timings.extend(self._encode_frame(self.command, extension=0))

        # Replace the last timing's space with the inter-frame gap
        if timings:
            last = timings[-1]
            timings[-1] = Timing(high_us=last.high_us, low_us=DENON_FRAME_GAP_US)

        # Second frame: inverted command, extension = 3
        timings.extend(
            self._encode_frame(~self.command & 0xFF, extension=3)
        )

        return timings
