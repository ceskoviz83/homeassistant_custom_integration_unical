"""Constants for the unical_owerone integration."""

import os

DOMAIN = "unical_owerone"
REGISTRY_JSON = ["sensors.json",
                 "digital_switch.json",
                 "status.json",
                 "setpoint.json"]
DEFAULT_SCAN_INTERVAL = 30

INTEGRATION_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(INTEGRATION_PATH, "config")
REGISTRY_PATH = [os.path.join(CONFIG_PATH, file) for file in REGISTRY_JSON]
