"""Constants for the unical_owerone integration."""

import os

DOMAIN = "unical_owerone"
REGISTRY_JSON = "sensors.json"
DEFAULT_SCAN_INTERVAL = 10

INTEGRATION_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(INTEGRATION_PATH, "config")
REGISTRY_PATH = os.path.join(CONFIG_PATH, "sensors.json")
