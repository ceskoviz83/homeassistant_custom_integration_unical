from .const import DOMAIN
from .coordinator import UnicalCoordinator
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from . import UnicalConfigEntry
from unical import EntityType, register
from .const import DOMAIN
from .coordinator import UnicalCoordinator
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry

import logging


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: UnicalConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: UnicalCoordinator = config_entry.runtime_data.coordinator

    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured

    select = [UnicalSelectEntity(coordinator,
                                 coordinator.data.registry[id])
                    for id in coordinator.data.registry
                    if coordinator.data.registry[id].entity_type == EntityType.SELECT]

    async_add_entities(select)

    pass


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


