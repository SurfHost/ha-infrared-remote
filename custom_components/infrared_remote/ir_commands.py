"""IR command factory with infrared-protocols support and NEC fallback.

Tries to use the official HA infrared-protocols library first.
Falls back to the built-in NEC encoder if the library is not available.
"""

from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

# Try to import the official infrared-protocols library
_HAS_IR_PROTOCOLS = False
try:
    from infrared_protocols.codes.lg.tv import LGTVCode, make_lg_tv_command  # noqa: F401

    _HAS_IR_PROTOCOLS = True
    _LOGGER.info("Using official infrared-protocols library for IR commands")
except ImportError:
    _LOGGER.info(
        "infrared-protocols library not available, using built-in NEC encoder"
    )

from .nec import NECCommand, RawTestCommand  # noqa: E402
from .const import (  # noqa: E402
    LG_TV_ADDRESS,
    LG_TV_COMMANDS,
    SAMSUNG_TV_ADDRESS,
    SAMSUNG_TV_COMMANDS,
)


def has_infrared_protocols() -> bool:
    """Return True if the official infrared-protocols library is available."""
    return _HAS_IR_PROTOCOLS


def make_lg_command(command_name: str) -> object | None:
    """Create an IR command for an LG TV.

    Uses infrared-protocols library if available, otherwise falls back
    to the built-in NEC encoder.
    """
    if _HAS_IR_PROTOCOLS:
        # Map our command names to LGTVCode enum values
        code_map = {
            "power": LGTVCode.POWER,
            "volume_up": LGTVCode.VOLUME_UP,
            "volume_down": LGTVCode.VOLUME_DOWN,
            "channel_up": LGTVCode.CHANNEL_UP,
            "channel_down": LGTVCode.CHANNEL_DOWN,
            "mute": LGTVCode.MUTE,
        }
        lg_code = code_map.get(command_name)
        if lg_code is not None:
            return make_lg_tv_command(lg_code)
        # Fall through to NEC for commands not in the official library

    code = LG_TV_COMMANDS.get(command_name)
    if code is None:
        return None
    return NECCommand(address=LG_TV_ADDRESS, command=code)


def make_samsung_command(command_name: str) -> object | None:
    """Create an IR command for a Samsung TV.

    Currently always uses built-in NEC encoder.
    Samsung support may be added to infrared-protocols in the future.
    """
    code = SAMSUNG_TV_COMMANDS.get(command_name)
    if code is None:
        return None
    return NECCommand(address=SAMSUNG_TV_ADDRESS, command=code)


def make_raw_test_command() -> RawTestCommand:
    """Create a raw test signal command."""
    return RawTestCommand()
