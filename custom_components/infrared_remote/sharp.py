"""Sharp/Denon IR protocol encoder.

Both Sharp and Denon use the same protocol family (Sharp invented it,
Denon licensed it). This module provides a single encoder for both.

Sharp/Denon protocol:
  - Carrier: 38 kHz
  - Pulse distance encoding
  - Bit mark: 320us
  - Bit 1: 320us mark, 1680us space (~2ms total)
  - Bit 0: 320us mark, 680us space (~1ms total)
  - Data: 5-bit address + 8-bit command + 1 expansion bit + 1 check bit
  - LSB first
  - Two frames: first normal, 40ms gap, second with inverted
    command + expansion + check bits
  - Stop bit: 320us mark after each frame

Sharp TV uses address 1, expansion bit = 1, check bit = 0.
Denon AVR uses address 2, expansion bit = 1, check bit = 0.
"""

from __future__ import annotations

from .const import (
    SHARP_BIT_MARK_US,
    SHARP_FRAME_GAP_US,
    SHARP_FREQUENCY_KHZ,
    SHARP_ONE_SPACE_US,
    SHARP_ZERO_SPACE_US,
)
from .nec import Timing


class SharpCommand:
    """Sharp/Denon protocol IR command that provides raw timings.

    Implements the same interface as NECCommand / InfraredCommand:
    - modulation: carrier frequency in kHz
    - repeat_count: number of times to repeat
    - get_raw_timings(): returns list of Timing objects

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
        """Initialize Sharp/Denon command.

        Args:
            address: 5-bit device address (0x00-0x1F)
            command: 8-bit command code (0x00-0xFF)
            expansion: expansion bit (1 for Sharp TV, 1 for Denon)
            check: check bit (0 for first frame, 1 for second)
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
        """Encode a single Sharp frame (15 bits + stop).

        Args:
            invert: if True, invert command, expansion, and check bits
                    (used for the second verification frame)
        """
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
        """Get the complete Sharp two-frame sequence as raw timings.

        Frame structure:
          [frame 1: addr + cmd + exp + chk + stop]
          [40ms gap]
          [frame 2: addr + ~cmd + ~exp + ~chk + stop]
        """
        timings: list[Timing] = []

        # First frame (normal)
        timings.extend(self._encode_frame(invert=False))

        # Replace the last timing's space with the 40ms inter-frame gap
        if timings:
            last = timings[-1]
            timings[-1] = Timing(high_us=last.high_us, low_us=SHARP_FRAME_GAP_US)

        # Second frame (inverted command/expansion/check)
        timings.extend(self._encode_frame(invert=True))

        return timings
