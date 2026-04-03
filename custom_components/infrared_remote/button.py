"""Button platform for Infrared Remote."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import infrared
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_ATTACH_TO_DEVICE,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_INFRARED_ENTITY_ID,
    DENON_AVR_COMMANDS,
    DEVICE_TYPE_DENON_AVR,
    DEVICE_TYPE_NEC_TV,
    DEVICE_TYPE_RAW_TEST,
    DEVICE_TYPE_SAMSUNG_TV,
    DEVICE_TYPE_SHARP_TV,
    DEVICE_TYPES,
    DOMAIN,
    LG_TV_COMMANDS,
    SAMSUNG_TV_COMMANDS,
    SHARP_TV_COMMANDS,
)
from .ir_commands import (
    make_denon_avr_command,
    make_lg_command,
    make_raw_test_command,
    make_samsung_command,
    make_sharp_tv_command,
)

_LOGGER = logging.getLogger(__name__)

BUTTON_ICONS = {
    "power": "mdi:power",
    "volume_up": "mdi:volume-plus",
    "volume_down": "mdi:volume-minus",
    "channel_up": "mdi:arrow-up-bold",
    "channel_down": "mdi:arrow-down-bold",
    "mute": "mdi:volume-mute",
    "input": "mdi:import",
    "ok": "mdi:check-circle",
    "up": "mdi:chevron-up",
    "down": "mdi:chevron-down",
    "left": "mdi:chevron-left",
    "right": "mdi:chevron-right",
    "back": "mdi:arrow-left",
    "home": "mdi:home",
    "menu": "mdi:menu",
    "play": "mdi:play",
    "pause": "mdi:pause",
    "stop": "mdi:stop",
    "test_signal": "mdi:access-point",
    "display": "mdi:monitor",
    "flashback": "mdi:history",
    "power_on": "mdi:power-on",
    "power_off": "mdi:power-off",
    "input_cd": "mdi:disc",
    "input_dvd": "mdi:disc-player",
    "input_tuner": "mdi:radio",
    "input_phono": "mdi:music-circle",
    "pure_direct": "mdi:surround-sound",
    "standard": "mdi:surround-sound-2-0",
    "0": "mdi:numeric-0",
    "1": "mdi:numeric-1",
    "2": "mdi:numeric-2",
    "3": "mdi:numeric-3",
    "4": "mdi:numeric-4",
    "5": "mdi:numeric-5",
    "6": "mdi:numeric-6",
    "7": "mdi:numeric-7",
    "8": "mdi:numeric-8",
    "9": "mdi:numeric-9",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Infrared Remote button entities."""
    emitter_entity_id = config_entry.data[CONF_INFRARED_ENTITY_ID]
    device_type = config_entry.data[CONF_DEVICE_TYPE]
    device_name = config_entry.data.get(
        CONF_DEVICE_NAME, DEVICE_TYPES.get(device_type, "IR Remote")
    )

    attach_device_id = config_entry.data.get(CONF_ATTACH_TO_DEVICE)
    if attach_device_id:
        dev_reg = dr.async_get(hass)
        dev_entry = dev_reg.async_get(attach_device_id)
        if dev_entry:
            device_info = DeviceInfo(identifiers=dev_entry.identifiers)
        else:
            _LOGGER.error("Target device %s not found", attach_device_id)
            return
    else:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=device_name,
            manufacturer="Infrared Remote",
            model=DEVICE_TYPES.get(device_type, device_type),
            sw_version="0.5.0",
        )

    entities: list[ButtonEntity] = []

    if device_type == DEVICE_TYPE_NEC_TV:
        for cmd_name in LG_TV_COMMANDS:
            entities.append(
                IRButton(
                    config_entry=config_entry,
                    emitter_entity_id=emitter_entity_id,
                    command_name=cmd_name,
                    command_factory=lambda name=cmd_name: make_lg_command(name),
                    device_info=device_info,
                )
            )
    elif device_type == DEVICE_TYPE_SAMSUNG_TV:
        for cmd_name in SAMSUNG_TV_COMMANDS:
            entities.append(
                IRButton(
                    config_entry=config_entry,
                    emitter_entity_id=emitter_entity_id,
                    command_name=cmd_name,
                    command_factory=lambda name=cmd_name: make_samsung_command(name),
                    device_info=device_info,
                )
            )
    elif device_type == DEVICE_TYPE_SHARP_TV:
        for cmd_name in SHARP_TV_COMMANDS:
            entities.append(
                IRButton(
                    config_entry=config_entry,
                    emitter_entity_id=emitter_entity_id,
                    command_name=cmd_name,
                    command_factory=lambda name=cmd_name: make_sharp_tv_command(name),
                    device_info=device_info,
                )
            )
    elif device_type == DEVICE_TYPE_DENON_AVR:
        for cmd_name in DENON_AVR_COMMANDS:
            entities.append(
                IRButton(
                    config_entry=config_entry,
                    emitter_entity_id=emitter_entity_id,
                    command_name=cmd_name,
                    command_factory=lambda name=cmd_name: make_denon_avr_command(name),
                    device_info=device_info,
                )
            )
    elif device_type == DEVICE_TYPE_RAW_TEST:
        entities.append(
            IRButton(
                config_entry=config_entry,
                emitter_entity_id=emitter_entity_id,
                command_name="test_signal",
                command_factory=make_raw_test_command,
                device_info=device_info,
            )
        )

    async_add_entities(entities)


class IRButton(ButtonEntity):
    """A button that sends a single IR command when pressed."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        emitter_entity_id: str,
        command_name: str,
        command_factory: Any,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the IR button."""
        self._emitter_entity_id = emitter_entity_id
        self._command_name = command_name
        self._command_factory = command_factory
        self._attr_name = command_name.replace("_", " ").title()
        self._attr_unique_id = f"{config_entry.entry_id}_{command_name}"
        self._attr_icon = BUTTON_ICONS.get(command_name, "mdi:remote")
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        """Send the IR command when the button is pressed."""
        command = self._command_factory()
        if command is None:
            _LOGGER.error("Failed to create IR command for '%s'", self._command_name)
            return

        _LOGGER.info(
            "Sending IR command '%s' via emitter %s",
            self._command_name,
            self._emitter_entity_id,
        )

        try:
            await infrared.async_send_command(
                self.hass,
                self._emitter_entity_id,
                command,
                context=self._context,
            )
        except HomeAssistantError as err:
            _LOGGER.error(
                "Failed to send IR command '%s' via %s: %s",
                self._command_name,
                self._emitter_entity_id,
                err,
            )
            raise
