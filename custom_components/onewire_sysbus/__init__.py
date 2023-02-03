"""The 1-Wire SysBus component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .onewirehub import OneWireHub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a 1-Wire hub for a config entry."""
    hass.data.setdefault(DOMAIN, {})

    onewirehub = OneWireHub(hass)
    await onewirehub.initialize(entry)

    hass.data[DOMAIN][entry.entry_id] = onewirehub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
