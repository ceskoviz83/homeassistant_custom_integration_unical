"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import UnicalConfigEntry
from unical import EntityType

from .coordinator import UnicalCoordinator
from .entities import UnicalClimate

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
    # This maybe different in your specific case, depending on how your data is

    climate = []

    climate += [UnicalClimate(coordinator,
                              setpoint=coordinator.data.registry[id]
                              )
                    for id in coordinator.data.registry
                    if coordinator.data.registry[id].entity_type == EntityType.CLIMATE]

    # Create the sensors.
    async_add_entities(climate)

