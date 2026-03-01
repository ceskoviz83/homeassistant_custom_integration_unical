"""Integration 101 Template integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_DEVICE_ID,
)
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from core.homeassistant.const import CONF_DEVICE_ID,CONF_HOST,CONF_PORT
#from .api import

from unical import register,Unical,modbus
from .const import DEFAULT_SCAN_INTERVAL,DOMAIN,REGISTRY_PATH

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceData:
    """Class to hold api data."""
    registry: register.RegistryMap
    controller_name: int = None

class UnicalCoordinator(DataUpdateCoordinator):
    """My example coordinator."""

    data: DeviceData

    def __init__(self,
                 hass: HomeAssistant,
                 config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.host = config_entry.data[CONF_HOST]
        self.port = config_entry.data[CONF_PORT]
        self.device_id = config_entry.data[CONF_DEVICE_ID]
        self.REGISTRY_FILE = REGISTRY_PATH

        # set variables from options.  You need a default here incase options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        # Initialise your api here


        self._modbus_client = modbus.Modbus(address = self.host,
                                            registry_file = self.REGISTRY_FILE,
                                            port = self.port,
                                            device_id = self.device_id)

        self.api = Unical(modbus_client=self._modbus_client)

        return

        #self.api = Unical(host=self.host,
        #                     port=self.port,
        #                     device_id=self.device_id)


    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            #if not self.api.connected:
            #    await self.hass.async_add_executor_job(self.api.connect)
            data = await self.hass.async_add_executor_job(self.api.read)
        #except APIAuthError as err:
        #    _LOGGER.error(err)
        #    raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # What is returned here is stored in self.data by the DataUpdateCoordinator
        return DeviceData(registry = data)


    def get_entity_by_id(self, id : int) -> register.Register | None:
        """Return device by device id."""
        # Called by the binary sensors and sensors to get their updated data from self.data
        try:
            return [ self.data.registry[address]  for address  in self.data.registry  if address == id][0]
        except IndexError:
            return None
    
