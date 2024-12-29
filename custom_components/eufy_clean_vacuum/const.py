"""Constants for the Eufy Clean Vacuum integration."""

DOMAIN = "eufy_clean_vacuum"

# Config flow
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Platforms
VACUUM = "vacuum"

# Services
SERVICE_CLEAN = "clean"
SERVICE_PAUSE = "pause"
SERVICE_STOP = "stop"
SERVICE_RETURN_TO_BASE = "return_to_base"

# States
STATE_CLEANING = "cleaning"
STATE_PAUSED = "paused"
STATE_IDLE = "idle"
STATE_RETURNING = "returning"
STATE_DOCKED = "docked"
STATE_ERROR = "error"

# Attributes
ATTR_STATUS = "status"
ATTR_BATTERY_LEVEL = "battery_level"
ATTR_ERROR_CODE = "error_code"
ATTR_FAN_SPEED = "fan_speed"
ATTR_CLEANING_TIME = "cleaning_time"
ATTR_CLEANED_AREA = "cleaned_area"

# Default values
DEFAULT_NAME = "Eufy Clean Vacuum"
