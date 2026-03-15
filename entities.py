import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from homeassistant.core import  callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.components.sensor import SensorDeviceClass

from .const import DOMAIN
from .coordinator import UnicalCoordinator

from unical import EntityType, register

_LOGGER = logging.getLogger(__name__)


class BadSensorImplementationException(Exception):
    pass


class UnicalSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""
    def __init__(self,
                 coordinator: UnicalCoordinator,
                 register : register.Register) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.register = register


    @property
    def device_id(self) -> str:
        return self.register.id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        res = self.coordinator.get_entity_by_id(self.device_id)

        if res is None :
            _LOGGER.error(f"Retrieved register is None - {self.device_id}")
        else:
            self.register = res

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
            }
        )


    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.register.name}"

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








class AnalogSensor(UnicalSensor):
    @property
    def native_value(self) -> int | float | None:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.

        if self.register is None:
            return None
        return float(self.register.value)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""

        if self.register is None:
            return ""

        return str(self.register.unit)


    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT



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

    _attr_icon = "mdi:percent"

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return "percentage"


class DurationSensor(AnalogSensor):
    """Implementation of a sensor."""

    _attr_icon = "mdi:clock"

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.DURATION


class EnumSensor(UnicalSensor):
    """Implementation of a sensor."""

    _attr_icon = "mdi:state-machine"

    def __init__(self, coordinator, register):
        super().__init__(coordinator, register)

        if self.register.has_taxonomy:
            self._attr_options = list(self.register.taxonomy.values())
        else:
            raise BadSensorImplementationException(f"Sensor {self.name} is enum_sensor but without Taxonomy")

    @property
    def native_value(self) -> int | None:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.

        res = None
        if self.register is None:
            return None

        val = str(self.register.value)

        for key , value in self.register.taxonomy.items():
            if val == key:
                res = value
                break

        return res

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.ENUM


class AlarmSensor(UnicalSensor):
    """Implementation of a sensor."""

    _attr_icon = "mdi:alert"

    def __init__(self, coordinator, register):
        super().__init__(coordinator, register)


        if not self.register.has_bits:
            raise BadSensorImplementationException(f"Sensor {self.name} is enum_sensor but without Taxonomy")

    @property
    def native_value(self) -> int | None:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.

        res = None
        if self.register is None:
            return None

        alarm_list = self.register.description

        if len(alarm_list) == 0:
            res = "No Alarms"
        else:
            res = " | ".join(alarm_list)

        return res

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.ENUM


from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)


class UnicalBinarySensor(BinarySensorEntity):
    """Representation of a Binary Sensor."""

    def __init__(self,
                 coordinator: UnicalCoordinator,
                 register : register.Register) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)

        self.coordinator :UnicalCoordinator = coordinator
        self.register = register

        if self.register is None:
            pass

        self.device_id = self.register.address

        self._attr_is_on = bool(self.register.value)


    @property
    def device_class(self) -> str:
        """Return device class."""
        return BinarySensorDeviceClass.RUNNING

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
        return f"{self.register.name}"

    @property
    def native_value(self) -> int | float | None:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.

        if self.register is None:
            return None

        return bool(self.register.value)

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is where you'd put your logic (API calls, file checks, etc.)
        """
        # Logic goes here. For example:
        # self._attr_is_on = some_check_function()

        reg = self.coordinator.get_entity_by_id(self.device_id)

        self.register.value = reg.value

        self._attr_is_on = bool(reg.value)

        pass

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)

class UnicalClimate(ClimateEntity):
    def __init__(self,
                 coordinator : CoordinatorEntity,
                 setpoint : register.Register):
        """Initialise """
        self.coordinator: UnicalCoordinator = coordinator
        self.setpoint_reg : register.Register= setpoint # valore di setpoint impostato

        id_actual = str(self.setpoint_reg.id_actual)

        if id_actual is None:
            raise ValueError("Actual address not set for Climate Entity")

        self.actual_reg : register.Register = self.coordinator.get_entity_by_id(id_actual) # valore attuale letto

        self._attr_supported_features = (
                ClimateEntityFeature.TARGET_TEMPERATURE |
                ClimateEntityFeature.TURN_ON |
                ClimateEntityFeature.TURN_OFF
        )

        # 1. Define only ONE mode so the UI can't switch it
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_modes = [str(HVACMode.HEAT)]

        # Initial values
        self._attr_temperature_unit =  UnitOfTemperature.CELSIUS
        self._attr_current_temperature = self.actual_reg.value
        self._attr_target_temperature = self.setpoint_reg.value

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
        """Return the name of the entity."""
        return f"{self.setpoint_reg.name}"

    @property
    def hvac_mode(self):
        """Always return the single allowed mode."""
        return self._attr_hvac_modes

    async def async_set_hvac_mode(self, hvac_mode):
        """Ignore requests to change mode, or just log them."""

        pass

    async def async_update(self):
        """Recupera gli ultimi dati dal dispositivo (polling)."""
        # Esempio: self._current_temp = await api.get_temp()
        act = self.coordinator.get_entity_by_id(self.actual_reg.id)
        if act is not None:
            self.actual_reg.value = act.value
            self._attr_current_temperature = self.actual_reg.value

        pass

    async def async_set_temperature(self, **kwargs):
        """This is where the slider logic lives."""

        if "temperature" in kwargs:
            setp = kwargs["temperature"]

            # 2. Attempt to write to the API
            success = await self._call_api_set_setpoint_temperature(setp)

            # 3. Update the UI state only if the API call was successful (Pessimistic Update)
            if success:
                self._attr_target_temperature = setp
                self.async_write_ha_state()
            else:
                _LOGGER.warning("Failed to update setpoint to %s", setp)


    async def _call_api_set_setpoint_temperature(self, value: str) -> bool:

        api = self.coordinator.api
        self.setpoint_reg.value = value

        try:
            api.write(self.register) # SCRIVI!
        except Exception as err:
            _LOGGER.error("Connection error while calling API: %s", err)
            return False



from homeassistant.components.select import SelectEntity


class UnicalSelectEntity(SelectEntity):
    """Representation of a custom select entity."""

    def __init__(self,
                 coordinator: UnicalCoordinator,
                 register : register.Register) -> None:
        """Initialize the entity."""
        self.coordinator = coordinator
        self.register : register.Register = register
        self.device_id = self.register.address
        self._attr_options = list(self.LOOKUP.keys())
        self._attr_current_option = self.register.description[0]
        return

    @property
    def api_value(self):
        return self.LOOKUP.get(self._attr_current_option)



    @property
    def LOOKUP(self) -> dict:
        return  {val: key for key, val in
                        self.register.taxonomy.items()}  # invert taxonomy. Key becomes frendly name. value is raw value


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
                    f"unical-{self.register.device}",
                )
            },
        )

    @property
    def current_option(self) -> str | None:
        """Return the current selected option"""
        reg =  self.coordinator.get_entity_by_id(self.device_id)
        self.register.raw = reg.raw
        self._attr_current_option = self.register.description[0]
        return self._attr_current_option


    async def async_select_option(self, option: str) -> None:
        """Handle the user making a selection in the UI."""

        # 1. Retrieve the technical value for the API
        raw_value = self.LOOKUP.get(option)

        if not raw_value:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        # 2. Attempt to write to the API
        success = await self._call_device_api(raw_value)

        # 3. Update the UI state only if the API call was successful (Pessimistic Update)
        if success:
            self._attr_current_option = option
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Failed to update device mode to %s", option)

    async def _call_device_api(self, value: str) -> bool:

        api = self.coordinator.api
        self.register.value = value
        try:
            api.write(self.register) # SCRIVI!
        except Exception as err:
            _LOGGER.error("Connection error while calling API: %s", err)
            return False

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.register.name}"

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.register.address}-{self.register.name}"


