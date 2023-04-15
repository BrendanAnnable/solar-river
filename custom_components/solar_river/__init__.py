"""The Samil Solar Inverter integration."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .solar_river.protocol import SamilImpl
from .solar_river.abstract import Samil
from .solar_river.fake import FakeSamil

from .const import DOMAIN, DATA_API_CLIENT

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Samil Solar Inverter from a config entry."""
    try:
        num_inverters = entry.data.get('num_inverters', None)
        api: Samil = await SamilImpl.discover_inverters(entry.data[CONF_HOST], entry.data[CONF_PORT], num_inverters)
        # api: Samil = await FakeSamil.discover_inverters(entry.data[CONF_HOST], entry.data[CONF_PORT])
    except Exception as ex:
        raise ConfigEntryNotReady from ex

    if not len(api.inverters):
        raise ConfigEntryNotReady('No inverters found')

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = { DATA_API_CLIENT: api }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
