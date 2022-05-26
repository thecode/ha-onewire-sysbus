"""Config flow for 1-Wire SysBus component."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_MOUNT_DIR, DEFAULT_SYSBUS_MOUNT_DIR, DOMAIN
from .onewirehub import InvalidPath, OneWireHub

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MOUNT_DIR, default=DEFAULT_SYSBUS_MOUNT_DIR): str,
    }
)


async def validate_input_mount_dir(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    hub = OneWireHub(hass)
    mount_dir = data[CONF_MOUNT_DIR]

    # Raises InvalidDir exception on failure
    await hub.check_mount_dir(mount_dir)

    return {"title": mount_dir}


class OneWireFlowHandler(ConfigFlow, domain=DOMAIN):  # type: ignore
    """Handle 1-Wire config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize 1-Wire config flow."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle 1-Wire config flow start."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Prevent duplicate entries
            await self.async_set_unique_id(user_input[CONF_MOUNT_DIR])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input_mount_dir(self.hass, user_input)
            except InvalidPath:
                errors["base"] = "invalid_path"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
