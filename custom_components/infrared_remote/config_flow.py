"""Config flow for the Infrared Remote integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import infrared
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.selector import (
    DeviceSelector,
    DeviceSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .const import (
    CONF_ATTACH_TO_DEVICE,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_INFRARED_ENTITY_ID,
    DEVICE_TYPES,
    DOMAIN,
)

SETUP_MODE_NEW = "new_device"
SETUP_MODE_ATTACH = "attach_to_device"


class InfraredRemoteConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Infrared Remote."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: choose setup mode."""
        if user_input is not None:
            if user_input["setup_mode"] == SETUP_MODE_ATTACH:
                return await self.async_step_attach()
            return await self.async_step_new_device()

        emitters = infrared.async_get_emitters(self.hass)
        if not emitters:
            return self.async_abort(reason="no_emitters")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("setup_mode", default=SETUP_MODE_NEW): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(
                                    value=SETUP_MODE_NEW,
                                    label="Create new device",
                                ),
                                SelectOptionDict(
                                    value=SETUP_MODE_ATTACH,
                                    label="Attach to existing device",
                                ),
                            ],
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
        )

    async def async_step_new_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle setup: create a new device."""
        if user_input is not None:
            entity_id = user_input[CONF_INFRARED_ENTITY_ID]
            device_type = user_input[CONF_DEVICE_TYPE]
            device_name = user_input.get(CONF_DEVICE_NAME, "").strip()

            if not device_name:
                device_name = DEVICE_TYPES.get(device_type, "IR Remote")

            await self.async_set_unique_id(f"{entity_id}_{device_type}_{device_name}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=device_name,
                data={
                    CONF_INFRARED_ENTITY_ID: entity_id,
                    CONF_DEVICE_TYPE: device_type,
                    CONF_DEVICE_NAME: device_name,
                },
            )

        emitters = infrared.async_get_emitters(self.hass)

        device_options = [
            SelectOptionDict(value=key, label=label)
            for key, label in DEVICE_TYPES.items()
        ]

        return self.async_show_form(
            step_id="new_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_INFRARED_ENTITY_ID): EntitySelector(
                        EntitySelectorConfig(
                            domain="infrared",
                            include_entities=emitters,
                        )
                    ),
                    vol.Required(
                        CONF_DEVICE_TYPE, default="nec_tv"
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=device_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_DEVICE_NAME, default=""
                    ): TextSelector(
                        TextSelectorConfig(type="text")
                    ),
                }
            ),
        )

    async def async_step_attach(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle setup: attach IR buttons to an existing device."""
        if user_input is not None:
            device_id = user_input[CONF_ATTACH_TO_DEVICE]
            entity_id = user_input[CONF_INFRARED_ENTITY_ID]
            device_type = user_input[CONF_DEVICE_TYPE]

            dev_reg = dr.async_get(self.hass)
            dev_entry = dev_reg.async_get(device_id)
            device_name = dev_entry.name if dev_entry else device_id

            await self.async_set_unique_id(
                f"{entity_id}_{device_type}_attach_{device_id}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"{device_name} IR Buttons",
                data={
                    CONF_INFRARED_ENTITY_ID: entity_id,
                    CONF_DEVICE_TYPE: device_type,
                    CONF_DEVICE_NAME: device_name,
                    CONF_ATTACH_TO_DEVICE: device_id,
                },
            )

        emitters = infrared.async_get_emitters(self.hass)

        device_options = [
            SelectOptionDict(value=key, label=label)
            for key, label in DEVICE_TYPES.items()
            if key != "raw_test"
        ]

        return self.async_show_form(
            step_id="attach",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ATTACH_TO_DEVICE): DeviceSelector(
                        DeviceSelectorConfig(
                            entity=[{"domain": "media_player"}],
                        )
                    ),
                    vol.Required(CONF_INFRARED_ENTITY_ID): EntitySelector(
                        EntitySelectorConfig(
                            domain="infrared",
                            include_entities=emitters,
                        )
                    ),
                    vol.Required(
                        CONF_DEVICE_TYPE, default="nec_tv"
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=device_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        entry = self._get_reconfigure_entry()
        is_attach = bool(entry.data.get(CONF_ATTACH_TO_DEVICE))

        if user_input is not None:
            entity_id = user_input[CONF_INFRARED_ENTITY_ID]
            device_type = user_input[CONF_DEVICE_TYPE]

            if is_attach:
                device_id = user_input[CONF_ATTACH_TO_DEVICE]
                dev_reg = dr.async_get(self.hass)
                dev_entry = dev_reg.async_get(device_id)
                device_name = dev_entry.name if dev_entry else device_id

                return self.async_update_reload_and_abort(
                    entry,
                    data={
                        CONF_INFRARED_ENTITY_ID: entity_id,
                        CONF_DEVICE_TYPE: device_type,
                        CONF_DEVICE_NAME: device_name,
                        CONF_ATTACH_TO_DEVICE: device_id,
                    },
                    reason="reconfigure_successful",
                )

            device_name = user_input.get(CONF_DEVICE_NAME, "").strip()
            if not device_name:
                device_name = DEVICE_TYPES.get(device_type, "IR Remote")

            return self.async_update_reload_and_abort(
                entry,
                title=device_name,
                data={
                    CONF_INFRARED_ENTITY_ID: entity_id,
                    CONF_DEVICE_TYPE: device_type,
                    CONF_DEVICE_NAME: device_name,
                },
                reason="reconfigure_successful",
            )

        emitters = infrared.async_get_emitters(self.hass)

        device_options = [
            SelectOptionDict(value=key, label=label)
            for key, label in DEVICE_TYPES.items()
            if not is_attach or key != "raw_test"
        ]

        if is_attach:
            schema = vol.Schema(
                {
                    vol.Required(CONF_ATTACH_TO_DEVICE): DeviceSelector(
                        DeviceSelectorConfig(
                            entity=[{"domain": "media_player"}],
                        )
                    ),
                    vol.Required(CONF_INFRARED_ENTITY_ID): EntitySelector(
                        EntitySelectorConfig(
                            domain="infrared",
                            include_entities=emitters,
                        )
                    ),
                    vol.Required(CONF_DEVICE_TYPE): SelectSelector(
                        SelectSelectorConfig(
                            options=device_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            )
        else:
            schema = vol.Schema(
                {
                    vol.Required(CONF_INFRARED_ENTITY_ID): EntitySelector(
                        EntitySelectorConfig(
                            domain="infrared",
                            include_entities=emitters,
                        )
                    ),
                    vol.Required(CONF_DEVICE_TYPE): SelectSelector(
                        SelectSelectorConfig(
                            options=device_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(CONF_DEVICE_NAME, default=""): TextSelector(
                        TextSelectorConfig(type="text")
                    ),
                }
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(schema, entry.data),
            description_placeholders={
                "emitter": entry.data.get(CONF_INFRARED_ENTITY_ID, "unknown"),
            },
        )
