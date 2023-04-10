import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .solar_river.abstract import Samil, SamilInverter
from .solar_river.model import InverterSpecs, InverterPVData
from .const import DOMAIN, DATA_API_CLIENT, SENSOR_TYPES, SCAN_INTERVAL, SolarRiverEntityDescription

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator, UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    api: Samil = hass.data[DOMAIN][entry.entry_id][DATA_API_CLIENT]

    sensors = []

    for inverter in api.inverters:
        try:
            specs = await inverter.get_specs()
            coordinator = SolarRiverCoordinator(hass, inverter, entry)
            await coordinator.async_config_entry_first_refresh()
            for description in SENSOR_TYPES:
                sensors.append(SolarRiverSensorEntity(coordinator, specs, description))
        except Exception as ex:
            _LOGGER.exception(f'Could not setup Solar River Inverter with serial {inverter.serial})', exc_info=ex)

    async_add_entities(sensors)


class SolarRiverCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, inverter: SamilInverter, entry: ConfigEntry):
        super().__init__(hass, _LOGGER, name="pv_data", update_interval=SCAN_INTERVAL)
        self.inverter = inverter
        self.name = entry.title
        self.host_url = f"http://{entry.data[CONF_HOST]}"

    async def _async_update_data(self):
        try:
            return await self.inverter.get_pv_data()
        except Exception as ex:
            raise UpdateFailed("Failed to fetch PV data from SolarRiver")


class SolarRiverSensorEntity(CoordinatorEntity[SolarRiverCoordinator], SensorEntity):
    def __init__(
            self,
            coordinator: SolarRiverCoordinator,
            specs: InverterSpecs,
            description: SolarRiverEntityDescription,
    ):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{coordinator.name} {description.name}"
        self._attr_unique_id = f"{specs.serial}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, specs.serial)},
            manufacturer=specs.manufacturer,
            sw_version=specs.firmware,
            model=specs.model,
            name=coordinator.name,
            configuration_url=coordinator.host_url,
        )

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated data from the coordinator."""
    #     self._attr_is_on = self.coordinator.data[self.idx]["state"]
    #     self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return getattr(self.coordinator.data, self.entity_description.key)

    # @property
    # def unique_id(self) -> str | None:
    #     return f"{self}"
