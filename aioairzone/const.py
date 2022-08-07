"""Airzone library constants."""

API_ACS_POINT = "acs_temp"
API_AIR_DEMAND = "air_demand"
API_COLD_ANGLE = "coldangle"
API_COLD_STAGE = "coldStage"
API_COLD_STAGES = "coldStages"
API_COOL_MAX_TEMP = "coolmaxtemp"
API_COOL_MIN_TEMP = "coolmintemp"
API_COOL_SET_POINT = "coolsetpoint"
API_DATA = "data"
API_DOUBLE_SET_POINT = "double_sp"
API_ERROR = "error"
API_ERRORS = "errors"
API_FLOOR_DEMAND = "floor_demand"
API_HEAT_ANGLE = "heatangle"
API_HEAT_MAX_TEMP = "heatmaxtemp"
API_HEAT_MIN_TEMP = "heatmintemp"
API_HEAT_SET_POINT = "heatsetpoint"
API_HEAT_STAGE = "heatStage"
API_HEAT_STAGES = "heatStages"
API_HUMIDITY = "humidity"
API_HVAC = "hvac"
API_INTERFACE = "interface"
API_MAC = "mac"
API_MANUFACTURER = "manufacturer"
API_MAX_TEMP = "maxTemp"
API_MC_CONNECTED = "mc_connected"
API_MIN_TEMP = "minTemp"
API_MODE = "mode"
API_MODES = "modes"
API_NAME = "name"
API_ON = "on"
API_POWER = "power"
API_ROOM_TEMP = "roomTemp"
API_SET_POINT = "setpoint"
API_SLEEP = "sleep"
API_SPEED = "speed"
API_SPEEDS = "speeds"
API_SYSTEM_FIRMWARE = "system_firmware"
API_SYSTEM_ID = "systemID"
API_SYSTEM_TYPE = "system_type"
API_SYSTEMS = "systems"
API_TEMP_STEP = "temp_step"
API_THERMOS_FIRMWARE = "thermos_firmware"
API_THERMOS_RADIO = "thermos_radio"
API_THERMOS_TYPE = "thermos_type"
API_UNITS = "units"
API_V1 = "api/v1"
API_WEBSERVER = "webserver"
API_WIFI = "wifi"
API_WIFI_CHANNEL = "wifi_channel"
API_WIFI_QUALITY = "wifi_quality"
API_WIFI_RSSI = "wifi_rssi"
API_WS_AIDOO = "ws_aidoo"
API_WS_AZ = "ws_az"
API_WS_FIRMWARE = "firmware"
API_WS_TYPE = "ws_type"
API_ZONE_ID = "zoneID"

API_ERROR_LOW_BATTERY = "Low battery"
API_ERROR_METHOD_NOT_SUPPORTED = "Method not provided or not supported"
API_ERROR_REQUEST_MALFORMED = "request malformed"
API_ERROR_SYSTEM_ID_NOT_AVAILABLE = "systemid not avaiable"
API_ERROR_SYSTEM_ID_OUT_RANGE = "systemid out of range"
API_ERROR_ZONE_ID_NOT_AVAILABLE = "zoneid not avaiable"
API_ERROR_ZONE_ID_NOT_PROVIDED = "zoneid not provided"
API_ERROR_ZONE_ID_OUT_RANGE = "zoneid out of range"

API_DOUBLE_SET_POINT_PARAMS = {
    API_COOL_MAX_TEMP,
    API_COOL_MIN_TEMP,
    API_COOL_SET_POINT,
    API_HEAT_MAX_TEMP,
    API_HEAT_MIN_TEMP,
    API_HEAT_SET_POINT,
}
API_SYSTEM_PARAMS = [
    API_MODE,
    API_SPEED,
]
API_ZONE_PARAMS = [
    API_COLD_ANGLE,
    API_COOL_SET_POINT,
    API_COLD_STAGE,
    API_HEAT_ANGLE,
    API_HEAT_SET_POINT,
    API_HEAT_STAGE,
    API_NAME,
    API_ON,
    API_SET_POINT,
    API_SLEEP,
]

AZD_AIR_DEMAND = "air-demand"
AZD_BATTERY_LOW = "battery-low"
AZD_CLAMP_METER = "clamp-meter"
AZD_COLD_ANGLE = "cold-angle"
AZD_COLD_STAGE = "cold-stage"
AZD_COLD_STAGES = "cold-stages"
AZD_COOL_TEMP_MAX = "cool-temp-max"
AZD_COOL_TEMP_MIN = "cool-temp-min"
AZD_COOL_TEMP_SET = "cool-temp-set"
AZD_DEMAND = "demand"
AZD_DOUBLE_SET_POINT = "double-set-point"
AZD_ENERGY = "energy"
AZD_ERRORS = "errors"
AZD_FIRMWARE = "firmware"
AZD_FULL_NAME = "full-name"
AZD_FLOOR_DEMAND = "floor-demand"
AZD_HEAT_ANGLE = "heat-angle"
AZD_HEAT_TEMP_MAX = "heat-temp-max"
AZD_HEAT_TEMP_MIN = "heat-temp-min"
AZD_HEAT_TEMP_SET = "heat-temp-set"
AZD_HEAT_STAGE = "heat-stage"
AZD_HEAT_STAGES = "heat-stages"
AZD_HUMIDITY = "humidity"
AZD_ID = "id"
AZD_INTERFACE = "interface"
AZD_MAC = "mac"
AZD_MANUFACTURER = "manufacturer"
AZD_MASTER = "master"
AZD_MODE = "mode"
AZD_MODEL = "model"
AZD_MODES = "modes"
AZD_NAME = "name"
AZD_ON = "on"
AZD_PROBLEMS = "problems"
AZD_SLEEP = "sleep"
AZD_SPEED = "speed"
AZD_SPEEDS = "speeds"
AZD_SYSTEM = "system"
AZD_SYSTEMS = "systems"
AZD_SYSTEMS_NUM = "num-systems"
AZD_TEMP = "temp"
AZD_TEMP_MAX = "temp-max"
AZD_TEMP_MIN = "temp-min"
AZD_TEMP_SET = "temp-set"
AZD_TEMP_STEP = "temp-step"
AZD_TEMP_UNIT = "temp-unit"
AZD_THERMOSTAT_FW = "thermostat-fw"
AZD_THERMOSTAT_MODEL = "thermostat-model"
AZD_THERMOSTAT_RADIO = "thermostat-radio"
AZD_WEBSERVER = "webserver"
AZD_WIFI_CHANNEL = "wifi-channel"
AZD_WIFI_QUALITY = "wifi-quality"
AZD_WIFI_RSSI = "wifi-rssi"
AZD_ZONES = "zones"
AZD_ZONES_NUM = "num-zones"

DEFAULT_PORT = 3000
DEFAULT_SYSTEM_ID = 0

ERROR_SYSTEM = "system"
ERROR_ZONE = "zone"

HTTP_CALL_TIMEOUT = 10

RAW_HVAC = "hvac"
RAW_SYSTEMS = "systems"
RAW_WEBSERVER = "webserver"

THERMOSTAT_RADIO = "Radio"
THERMOSTAT_WIRED = "Wired"
