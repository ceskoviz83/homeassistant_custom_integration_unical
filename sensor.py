"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature,UnitOfPressure
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.sensor import SensorDeviceClass
from . import UnicalConfigEntry
from unical import EntityType, register
from .const import DOMAIN
from .coordinator import UnicalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: UnicalConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: UnicalCoordinator = config_entry.runtime_data.coordinator

    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured

    temp_sensors = [TempSensor(coordinator,   coordinator.data.registry[id])
                    for id in coordinator.data.registry
                    if coordinator.data.registry[id].entity_type == EntityType.TEMP_SENSOR]

    percent_sensor = [PercentageSensor(coordinator,   coordinator.data.registry[id])
                      for id in coordinator.data.registry
                      if coordinator.data.registry[id].entity_type == EntityType.PERCENT_SENSOR]

    press_sensor = [PressureSensor(coordinator,   coordinator.data.registry[id])
                    for id in coordinator.data.registry
                    if coordinator.data.registry[id].entity_type == EntityType.PRES_SENSOR]


    duration_sensor = [DurationSensor(coordinator,   coordinator.data.registry[id])
                       for id in coordinator.data.registry
                       if coordinator.data.registry[id].entity_type == EntityType.DURATION_SENSOR]

    # Create the sensors.

    async_add_entities(temp_sensors + percent_sensor + press_sensor + duration_sensor)


class AnalogSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(self,
                 coordinator: UnicalCoordinator,
                 register : register.Register) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.register = register

        if self.register is None:
            pass

        self.device_id = self.register.address

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.register = self.coordinator.get_entity_by_id(self.device_id)
        _LOGGER.debug("Device: %s", self.register)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        raise NotImplementedError("you mus implement this method")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return DeviceInfo(
            name=f"{self.register.device}",
            manufacturer="Unical",
            model="OwerOne 120R",
            sw_version="1.0",
            identifiers={
                (
                    DOMAIN,
                    f"{self.coordinator.data.controller_name}-{self.register.device}",
                )
            },
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.register.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.register.value)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""

        if self.register is None:
            pass

        return str(self.register.unit)


    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.register.address}-{self.register.name}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["extra_info"] = "Extra Info"
        return attrs

class TempSensor(AnalogSensor):
    """Implementation of a sensor."""

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.TEMPERATURE


class PressureSensor(AnalogSensor):
    """Implementation of a sensor."""


    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.PRESSURE

class PercentageSensor(AnalogSensor):
    """Implementation of a sensor."""

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.SPEED


class DurationSensor(AnalogSensor):
    """Implementation of a sensor."""

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.DURATION