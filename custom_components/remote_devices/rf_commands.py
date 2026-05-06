"""RF command factory for the Remote Devices integration.

Provides RawBroadlinkRFCommand for devices we control via captured Broadlink RF
packets (e.g. the Airwit Plafondventilator). Mirrors the IR-side
`RawBroadlinkCommand` from nec.py but produces a `RadioFrequencyCommand`
compatible object instead of an `InfraredCommand`.

Pre-decoded once at import: looking up an Airwit command at button-press time
returns the cached `RawBroadlinkRFCommand` instance.
"""

from __future__ import annotations

from homeassistant.components.radio_frequency import ModulationType

from .broadlink_decode import Timing, decode_broadlink_b64_to_timings
from .const import AIRWIT_FAN_BROADLINK_RF_CODES, AIRWIT_FAN_FREQUENCY_HZ


class RawBroadlinkRFCommand:
    """RF command decoded from a Broadlink-learned base64 packet.

    Implements the `RadioFrequencyCommand` interface:
    - frequency: int (Hz)
    - modulation: ModulationType
    - repeat_count: int
    - get_raw_timings() -> list[Timing]
    """

    def __init__(
        self,
        b64_code: str,
        frequency: int = AIRWIT_FAN_FREQUENCY_HZ,
        repeat_count: int = 0,
    ) -> None:
        """Initialize from a Broadlink base64-encoded RF packet."""
        self.frequency = frequency
        self.modulation = ModulationType.OOK
        self.repeat_count = repeat_count
        # RF signals contain long internal gaps (sync→data) that are NOT
        # repeat-frame boundaries. Decode the full packet without stripping.
        self._timings = decode_broadlink_b64_to_timings(b64_code, strip_repeats=False)

    def get_raw_timings(self) -> list[Timing]:
        """Return the decoded mark/space timings."""
        return self._timings


# Pre-decode every Airwit code once at import.
AIRWIT_FAN_COMMANDS: dict[str, RawBroadlinkRFCommand] = {
    name: RawBroadlinkRFCommand(b64) for name, b64 in AIRWIT_FAN_BROADLINK_RF_CODES.items()
}


def make_airwit_fan_command(name: str) -> RawBroadlinkRFCommand | None:
    """Return the cached RF command for the named Airwit button, or None."""
    return AIRWIT_FAN_COMMANDS.get(name)
