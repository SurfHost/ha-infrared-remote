"""Sharp and Denon IR protocol encoders.

Both classes inherit from the official `InfraredCommand` ABC and emit timings
in the standard flat `list[int]` (signed-µs) format expected by HA core.

Despite being in the same protocol family, Sharp and Denon use different
timing values and slightly different frame structures. This module provides
separate encoders for each.

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

from homeassistant.components.infrared import InfraredCommand

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


class SharpCommand(InfraredCommand):
    """Sharp protocol IR command (5-bit addr + 8-bit cmd, two-frame)."""

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
        super().__init__(modulation=SHARP_FREQUENCY_KHZ, repeat_count=repeat_count)
        self.address = address & 0x1F
        self.command = command & 0xFF
        self.expansion = expansion & 0x01
        self.check = check & 0x01

    def _encode_bits_lsb(self, value: int, num_bits: int) -> list[int]:
        """Encode bits as Sharp mark/space pairs, LSB first."""
        timings: list[int] = []
        for bit_idx in range(num_bits):
            timings.append(SHARP_BIT_MARK_US)
            if (value >> bit_idx) & 1:
                timings.append(-SHARP_ONE_SPACE_US)
            else:
                timings.append(-SHARP_ZERO_SPACE_US)
        return timings

    def _encode_frame(self, invert: bool = False) -> list[int]:
        """Encode a single Sharp frame (15 bits + stop)."""
        timings: list[int] = []
        timings.extend(self._encode_bits_lsb(self.address, 5))
        cmd = (~self.command & 0xFF) if invert else self.command
        timings.extend(self._encode_bits_lsb(cmd, 8))
        exp = (self.expansion ^ 1) if invert else self.expansion
        timings.extend(self._encode_bits_lsb(exp, 1))
        chk = (self.check ^ 1) if invert else self.check
        timings.extend(self._encode_bits_lsb(chk, 1))
        # Stop bit (mark + a "zero" space placeholder; caller may overwrite)
        timings.append(SHARP_BIT_MARK_US)
        timings.append(-SHARP_ZERO_SPACE_US)
        return timings

    def get_raw_timings(self) -> list[int]:
        """Return the two-frame Sharp sequence as signed-µs timings."""
        timings = self._encode_frame(invert=False)
        # Replace the last (stop) space with the inter-frame gap
        if timings:
            timings[-1] = -SHARP_FRAME_GAP_US
        timings.extend(self._encode_frame(invert=True))
        return timings


class DenonCommand(InfraredCommand):
    """Denon protocol IR command (5-bit addr + 8-bit cmd + 2-bit ext, two-frame)."""

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
        super().__init__(modulation=DENON_FREQUENCY_KHZ, repeat_count=repeat_count)
        self.address = address & 0x1F
        self.command = command & 0xFF

    def _encode_bits_lsb(self, value: int, num_bits: int) -> list[int]:
        """Encode bits as Denon mark/space pairs, LSB first."""
        timings: list[int] = []
        for bit_idx in range(num_bits):
            timings.append(DENON_BIT_MARK_US)
            if (value >> bit_idx) & 1:
                timings.append(-DENON_ONE_SPACE_US)
            else:
                timings.append(-DENON_ZERO_SPACE_US)
        return timings

    def _encode_frame(self, command: int, extension: int) -> list[int]:
        """Encode a single Denon frame: 15 data bits + stop (no header)."""
        timings: list[int] = []
        timings.extend(self._encode_bits_lsb(self.address, 5))
        timings.extend(self._encode_bits_lsb(command, 8))
        timings.extend(self._encode_bits_lsb(extension, 2))
        # Stop bit
        timings.append(DENON_BIT_MARK_US)
        timings.append(-DENON_ZERO_SPACE_US)
        return timings

    def get_raw_timings(self) -> list[int]:
        """Return the two-frame Denon sequence as signed-µs timings.

        Frame 1: address + command + ext=0 + stop
        Gap: 43.5ms
        Frame 2: address + ~command + ext=3 + stop
        """
        timings = self._encode_frame(self.command, extension=0)
        # Replace the last (stop) space with the inter-frame gap
        if timings:
            timings[-1] = -DENON_FRAME_GAP_US
        timings.extend(self._encode_frame(~self.command & 0xFF, extension=3))
        return timings
