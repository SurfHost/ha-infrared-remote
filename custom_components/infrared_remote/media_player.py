"""Media player platform for Infrared Remote."""

from __future__ import annotations

import logging

from homeassistant.components import infrared
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_INFRARED_ENTITY_ID,
    DEVICE_TYPE_NEC_TV,
    DEVICE_TYPE_RAW_TEST,
    DEVICE_TYPE_SAMSUNG_TV,
    DEVICE_TYPES,
    DOMAIN,
    LG_TV_ADDRESS,
    LG_TV_COMMANDS,
    SAMSUNG_TV_ADDRESS,
    SAMSUNG_TV_COMMANDS,
)
from .nec import NECCommand

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Infrared Remote media player entities."""
    emitter_entity_id = config_entry.data[CONF_INFRARED_ENTITY_ID]
    device_type = config_entry.data[CONF_DEVICE_TYPE]
    device_name = config_entry.data.get(
        CONF_DEVICE_NAME, DEVICE_TYPES.get(device_type, "IR Remote")
    )

    if device_type == DEVICE_TYPE_RAW_TEST:
        return

    if device_type == DEVICE_TYPE_NEC_TV:
        address = LG_TV_ADDRESS
        commands = LG_TV_COMMANDS
    elif device_type == DEVICE_TYPE_SAMSUNG_TV:
        address = SAMSUNG_TV_ADDRESS
        commands = SAMSUNG_TV_COMMANDS
    else:
        return

    device_info = DeviceInfo(
        identifiers={(DOMAIN, config_entry.entry_id)},
        name=device_name,
        manufacturer="Infrared Remote",
        model=DEVICE_TYPES.get(device_type, device_type),
        sw_version="0.2.0",
    )

    async_add_entities(
        [
            IRMediaPlayer(
                config_entry=config_entry,
                emitter_entity_id=emitter_entity_id,
                address=address,
                commands=commands,
                device_info=device_info,
            )
        ]
    )


class IRMediaPlayer(MediaPlayerEntity):
    """A media player entity that controls a TV via IR."""

    _attr_has_entity_name = True
    _attr_name = "TV"
    _attr_icon = "mdi:television"
    _attr_assumed_state = True
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
    )

    def __init__(
        self,
        config_entry: ConfigEntry,
        emitter_entity_id: str,
        address: int,
        commands: dict[str, int],
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the IR media player."""
        self._emitter_entity_id = emitter_entity_id
        self._address = address
        self._commands = commands
        self._attr_unique_id = f"{config_entry.entry_id}_media_player"
        self._attr_device_info = device_info
        self._attr_state = MediaPlayerState.OFF
        self._attr_is_volume_muted = False

    async def _send_command(self, command_name: str) -> None:
        """Send an IR command by name."""
        code = self._commands.get(command_name)
        if code is None:
            _LOGGER.warning("Command '%s' not found in command set", command_name)
            return

        command = NECCommand(address=self._address, command=code)

        _LOGGER.debug(
            "Media player sending '%s' (addr=0x%02X, cmd=0x%02X)",
            command_name,
            self._address,
            code,
        )

        await infrared.async_send_command(
            self.hass,
            self._emitter_entity_id,
            command,
            context=self._context,
        )

    async def async_turn_on(self) -> None:
        """Turn the TV on."""
        await self._send_command("power")
        self._attr_state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the TV off."""
        await self._send_command("power")
        self._attr_state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_volume_up(self) -> None:
        """Turn volume up."""
        await self._send_command("volume_up")

    async def async_volume_down(self) -> None:
        """Turn volume down."""
        await self._send_command("volume_down")

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute/unmute the TV."""
        await self._send_command("mute")
        self._attr_is_volume_muted = mute
        self.async_write_ha_state()
