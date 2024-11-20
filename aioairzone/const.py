"""Airzone library constants."""

from typing import Final

from packaging.version import Version

API_ACS_MAX_TEMP: Final[str] = "acs_maxtemp"
API_ACS_MIN_TEMP: Final[str] = "acs_mintemp"
API_ACS_ON: Final[str] = "acs_power"
API_ACS_POWER_MODE: Final[str] = "acs_powerful"
API_ACS_SET_POINT: Final[str] = "acs_setpoint"
API_ACS_TEMP: Final[str] = "acs_temp"
API_AIR_DEMAND: Final[str] = "air_demand"
API_ANTI_FREEZE: Final[str] = "antifreeze"
API_COLD_ANGLE: Final[str] = "coldangle"
API_COLD_DEMAND: Final[str] = "cold_demand"
API_COLD_STAGE: Final[str] = "coldStage"
API_COLD_STAGES: Final[str] = "coldStages"
API_COOL_MAX_TEMP: Final[str] = "coolmaxtemp"
API_COOL_MIN_TEMP: Final[str] = "coolmintemp"
API_COOL_SET_POINT: Final[str] = "coolsetpoint"
API_DATA: Final[str] = "data"
API_DEMO: Final[str] = "demo"
API_DRIVER: Final[str] = "driver"
API_DOUBLE_SET_POINT: Final[str] = "double_sp"
API_ECO_ADAPT: Final[str] = "eco_adapt"
API_ERROR: Final[str] = "error"
API_ERRORS: Final[str] = "errors"
API_FLOOR_DEMAND: Final[str] = "floor_demand"
API_HEAT_ANGLE: Final[str] = "heatangle"
API_HEAT_DEMAND: Final[str] = "heat_demand"
API_HEAT_MAX_TEMP: Final[str] = "heatmaxtemp"
API_HEAT_MIN_TEMP: Final[str] = "heatmintemp"
API_HEAT_SET_POINT: Final[str] = "heatsetpoint"
API_HEAT_STAGE: Final[str] = "heatStage"
API_HEAT_STAGES: Final[str] = "heatStages"
API_HUMIDITY: Final[str] = "humidity"
API_HVAC: Final[str] = "hvac"
API_INTEGRATION: Final[str] = "integration"
API_INTERFACE: Final[str] = "interface"
API_MAC: Final[str] = "mac"
API_MANUFACTURER: Final[str] = "manufacturer"
API_MASTER_ZONE_ID: Final[str] = "master_zoneID"
API_MAX_TEMP: Final[str] = "maxTemp"
API_MC_CONNECTED: Final[str] = "mc_connected"
API_MIN_TEMP: Final[str] = "minTemp"
API_MODE: Final[str] = "mode"
API_MODES: Final[str] = "modes"
API_NAME: Final[str] = "name"
API_ON: Final[str] = "on"
API_POWER: Final[str] = "power"
API_ROOM_TEMP: Final[str] = "roomTemp"
API_SET_POINT: Final[str] = "setpoint"
API_SLEEP: Final[str] = "sleep"
API_SPEED: Final[str] = "speed"
API_SPEEDS: Final[str] = "speeds"
API_SYSTEM_FIRMWARE: Final[str] = "system_firmware"
API_SYSTEM_ID: Final[str] = "systemID"
API_SYSTEM_TYPE: Final[str] = "system_type"
API_SYSTEMS: Final[str] = "systems"
API_TEMP_STEP: Final[str] = "temp_step"
API_THERMOS_FIRMWARE: Final[str] = "thermos_firmware"
API_THERMOS_RADIO: Final[str] = "thermos_radio"
API_THERMOS_TYPE: Final[str] = "thermos_type"
API_UNITS: Final[str] = "units"
API_V1: Final[str] = "api/v1"
API_VERSION: Final[str] = "version"
API_WEBSERVER: Final[str] = "webserver"
API_WIFI: Final[str] = "wifi"
API_WIFI_CHANNEL: Final[str] = "wifi_channel"
API_WIFI_QUALITY: Final[str] = "wifi_quality"
API_WIFI_RSSI: Final[str] = "wifi_rssi"
API_WS_AIDOO: Final[str] = "ws_aidoo"
API_WS_AZ: Final[str] = "ws_az"
API_WS_FIRMWARE: Final[str] = "ws_firmware"
API_WS_TYPE: Final[str] = "ws_type"
API_ZONE_ID: Final[str] = "zoneID"

API_ERROR_HOT_WATER_NOT_CONNECTED: Final[str] = "acs not connected"
API_ERROR_IAQ_SENSOR_ID_NOT_AVAILABLE: Final[str] = "iaqsensorid not available"
API_ERROR_LOW_BATTERY: Final[str] = "Low battery"
API_ERROR_METHOD_NOT_SUPPORTED: Final[str] = "Method not provided or not supported"
API_ERROR_REQUEST_MALFORMED: Final[str] = "request malformed"
API_ERROR_SYSTEM_ID_NOT_AVAILABLE: Final[str] = "systemid not avaiable"
API_ERROR_SYSTEM_ID_NOT_PROVIDED: Final[str] = "systemid not provided"
API_ERROR_SYSTEM_ID_OUT_RANGE: Final[str] = "systemid out of range"
API_ERROR_ZONE_ID_NOT_AVAILABLE: Final[str] = "zoneid not avaiable"
API_ERROR_ZONE_ID_NOT_PROVIDED: Final[str] = "zoneid not provided"
API_ERROR_ZONE_ID_OUT_RANGE: Final[str] = "zoneid out of range"

API_DHW_PARAMS: Final[list[str]] = [
    API_ACS_ON,
    API_ACS_POWER_MODE,
    API_ACS_SET_POINT,
]
API_DOUBLE_SET_POINT_PARAMS: Final[set[str]] = {
    API_COOL_MAX_TEMP,
    API_COOL_MIN_TEMP,
    API_COOL_SET_POINT,
    API_HEAT_MAX_TEMP,
    API_HEAT_MIN_TEMP,
    API_HEAT_SET_POINT,
}
API_NO_FEEDBACK_PARAMS: Final[list[str]] = [
    API_MODE,
]
API_SYSTEM_PARAMS: Final[list[str]] = [
    API_MODE,
    API_SPEED,
]
API_ZONE_PARAMS: Final[list[str]] = [
    API_COOL_SET_POINT,
    API_COLD_ANGLE,
    API_COLD_STAGE,
    API_HEAT_ANGLE,
    API_HEAT_SET_POINT,
    API_HEAT_STAGE,
    API_NAME,
    API_ON,
    API_SET_POINT,
    API_SLEEP,
]

AZD_ABS_TEMP_MAX: Final[str] = "absolute-temp-max"
AZD_ABS_TEMP_MIN: Final[str] = "absolute-temp-min"
AZD_ACTION: Final[str] = "action"
AZD_AIR_DEMAND: Final[str] = "air-demand"
AZD_ANTI_FREEZE: Final[str] = "anti-freeze"
AZD_AVAILABLE: Final[str] = "available"
AZD_BATTERY_LOW: Final[str] = "battery-low"
AZD_CLAMP_METER: Final[str] = "clamp-meter"
AZD_COLD_ANGLE: Final[str] = "cold-angle"
AZD_COLD_DEMAND: Final[str] = "cold-demand"
AZD_COLD_STAGE: Final[str] = "cold-stage"
AZD_COLD_STAGES: Final[str] = "cold-stages"
AZD_COOL_TEMP_MAX: Final[str] = "cool-temp-max"
AZD_COOL_TEMP_MIN: Final[str] = "cool-temp-min"
AZD_COOL_TEMP_SET: Final[str] = "cool-temp-set"
AZD_DEMAND: Final[str] = "demand"
AZD_DOUBLE_SET_POINT: Final[str] = "double-set-point"
AZD_ECO_ADAPT: Final[str] = "eco-adapt"
AZD_ENERGY: Final[str] = "energy"
AZD_ERRORS: Final[str] = "errors"
AZD_FIRMWARE: Final[str] = "firmware"
AZD_FULL_NAME: Final[str] = "full-name"
AZD_FLOOR_DEMAND: Final[str] = "floor-demand"
AZD_HEAT_ANGLE: Final[str] = "heat-angle"
AZD_HEAT_DEMAND: Final[str] = "heat-demand"
AZD_HEAT_TEMP_MAX: Final[str] = "heat-temp-max"
AZD_HEAT_TEMP_MIN: Final[str] = "heat-temp-min"
AZD_HEAT_TEMP_SET: Final[str] = "heat-temp-set"
AZD_HEAT_STAGE: Final[str] = "heat-stage"
AZD_HEAT_STAGES: Final[str] = "heat-stages"
AZD_HOT_WATER: Final[str] = "hot-water"
AZD_HUMIDITY: Final[str] = "humidity"
AZD_ID: Final[str] = "id"
AZD_INTERFACE: Final[str] = "interface"
AZD_MAC: Final[str] = "mac"
AZD_MANUFACTURER: Final[str] = "manufacturer"
AZD_MASTER: Final[str] = "master"
AZD_MASTER_SYSTEM_ZONE: Final[str] = "master-system-zone"
AZD_MASTER_ZONE: Final[str] = "master-zone"
AZD_MODE: Final[str] = "mode"
AZD_MODEL: Final[str] = "model"
AZD_MODES: Final[str] = "modes"
AZD_NAME: Final[str] = "name"
AZD_OPERATION: Final[str] = "operation"
AZD_OPERATIONS: Final[str] = "operations"
AZD_ON: Final[str] = "on"
AZD_POWER_MODE: Final[str] = "power-mode"
AZD_PROBLEMS: Final[str] = "problems"
AZD_SLEEP: Final[str] = "sleep"
AZD_SPEED: Final[str] = "speed"
AZD_SPEEDS: Final[str] = "speeds"
AZD_SYSTEM: Final[str] = "system"
AZD_SYSTEMS: Final[str] = "systems"
AZD_SYSTEMS_NUM: Final[str] = "num-systems"
AZD_TEMP: Final[str] = "temp"
AZD_TEMP_MAX: Final[str] = "temp-max"
AZD_TEMP_MIN: Final[str] = "temp-min"
AZD_TEMP_SET: Final[str] = "temp-set"
AZD_TEMP_STEP: Final[str] = "temp-step"
AZD_TEMP_UNIT: Final[str] = "temp-unit"
AZD_THERMOSTAT_FW: Final[str] = "thermostat-fw"
AZD_THERMOSTAT_MODEL: Final[str] = "thermostat-model"
AZD_THERMOSTAT_RADIO: Final[str] = "thermostat-radio"
AZD_VERSION: Final[str] = "version"
AZD_WEBSERVER: Final[str] = "webserver"
AZD_WIFI_CHANNEL: Final[str] = "wifi-channel"
AZD_WIFI_QUALITY: Final[str] = "wifi-quality"
AZD_WIFI_RSSI: Final[str] = "wifi-rssi"
AZD_ZONES: Final[str] = "zones"
AZD_ZONES_NUM: Final[str] = "num-zones"

API_BUG_MIN_TEMP_FAH: Final[int] = 32
API_BUG_MAX_TEMP_FAH: Final[int] = 140

DEFAULT_PORT: Final[int] = 3000
DEFAULT_SYSTEM_ID: Final[int] = 0
DEFAULT_TEMP_MAX_CELSIUS: Final[float] = 30.0
DEFAULT_TEMP_MAX_FAHRENHEIT: Final[float] = 86.0
DEFAULT_TEMP_MIN_CELSIUS: Final[float] = 15.0
DEFAULT_TEMP_MIN_FAHRENHEIT: Final[float] = 60.0
DEFAULT_TEMP_STEP_CELSIUS: Final[float] = 0.5
DEFAULT_TEMP_STEP_FAHRENHEIT: Final[float] = 1.0

ERROR_SYSTEM: Final[str] = "system"
ERROR_ZONE: Final[str] = "zone"

HTTP_CALL_TIMEOUT: Final[int] = 10
HTTP_MAX_REQUESTS: Final[int] = 1
HTTP_QUIRK_VERSION: Final[Version] = Version("9.99")  # Fix version is still unknown

RAW_DEMO: Final[str] = "demo"
RAW_DHW: Final[str] = "dhw"
RAW_HEADERS: Final[str] = "headers"
RAW_HVAC: Final[str] = "hvac"
RAW_HTTP: Final[str] = "http"
RAW_INTEGRATION: Final[str] = "integration"
RAW_QUIRKS: Final[str] = "quirks"
RAW_REASON: Final[str] = "reason"
RAW_STATUS: Final[str] = "status"
RAW_SYSTEMS: Final[str] = "systems"
RAW_VERSION: Final[str] = "version"
RAW_WEBSERVER: Final[str] = "webserver"

THERMOSTAT_RADIO: Final[str] = "Radio"
THERMOSTAT_WIRED: Final[str] = "Wired"
