"""Shared helper for decoding Broadlink-learned base64 packets to raw timings.

Used by both IR commands (nec.RawBroadlinkCommand) and RF commands
(rf_commands.RawBroadlinkRFCommand). The wire format is identical for IR
and RF, only the type byte differs.
"""

from __future__ import annotations

import base64
import struct
from dataclasses import dataclass

# Broadlink time quantum: 269/8192 seconds ~= 32.84 µs per tick.
BROADLINK_TICK_US = 269000 / 8192


@dataclass
class Timing:
    """A single mark/space timing pair (microseconds)."""

    high_us: int
    low_us: int


def decode_broadlink_b64_to_timings(
    b64_code: str,
    *,
    strip_repeats: bool = True,
) -> list[Timing]:
    """Decode a Broadlink base64 packet to a list of mark/space Timing pairs.

    By default (strip_repeats=True), stops at the first inter-frame gap
    longer than 50 ms — appropriate for IR codes where the captured packet
    contains repeat frames separated by long gaps.

    For RF codes, pass strip_repeats=False: RF signals routinely contain long
    (100+ ms) gaps between sync pulse and data burst that are part of the
    intended signal, not repeat-frame boundaries.
    """
    data = base64.b64decode(b64_code)
    length = struct.unpack("<H", data[2:4])[0]
    timing_data = data[4 : 4 + length]

    raw_us: list[int] = []
    i = 0
    while i < len(timing_data):
        if timing_data[i] == 0x00 and i + 2 < len(timing_data):
            val = (timing_data[i + 1] << 8) | timing_data[i + 2]
            i += 3
        else:
            val = timing_data[i]
            i += 1
        raw_us.append(round(val * BROADLINK_TICK_US))

    timings: list[Timing] = []
    idx = 0
    while idx + 1 < len(raw_us):
        mark = raw_us[idx]
        space = raw_us[idx + 1]
        if strip_repeats and space > 50000:
            # End of first frame — skip repeat frames.
            timings.append(Timing(high_us=mark, low_us=mark))
            break
        timings.append(Timing(high_us=mark, low_us=space))
        idx += 2

    return timings
