"""Config flow for the Infrared Remote integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import infrared
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
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
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_INFRARED_ENTITY_ID,
    DEVICE_TYPES,
    DOMAIN,
)


class InfraredRemoteConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Infrared Remote."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}

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

        if not emitters:
            return self.async_abort(reason="no_emitters")

        device_options = [
            SelectOptionDict(value=key, label=label)
            for key, label in DEVICE_TYPES.items()
        ]

        return self.async_show_form(
            step_id="user",
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
            errors=errors,
        )
