"""Airzone library constants."""

API_ACS_POINT = "acs_temp"
API_AIR_DEMAND = "air_demand"
API_COLD_STAGE = "coldStage"
API_COLD_STAGES = "coldStages"
API_COOL_SET_POINT = "coolsetpoint"
API_DATA = "data"
API_ERRORS = "errors"
API_FLOOR_DEMAND = "floor_demand"
API_HEAT_STAGE = "heatStage"
API_HEAT_STAGES = "heatStages"
API_HUMIDITY = "humidity"
API_HVAC = "hvac"
API_MAX_TEMP = "maxTemp"
API_MIN_TEMP = "minTemp"
API_MODE = "mode"
API_MODES = "modes"
API_NAME = "name"
API_ON = "on"
API_ROOM_TEMP = "roomTemp"
API_SET_POINT = "setpoint"
API_SYSTEM_ID = "systemID"
API_SYSTEMS = "systems"
API_UNITS = "units"
API_V1 = "api/v1"
API_ZONE_ID = "zoneID"

API_ERROR_SYSTEM_ID_OUT_RANGE = "systemid out of range"
API_ERROR_ZONE_ID_NOT_AVAILABLE = "zoneid not avaiable"
API_ERROR_ZONE_ID_OUT_RANGE = "zoneid out of range"

API_SYSTEM_PARAMS = [API_MODE]
API_ZONE_PARAMS = [
    API_COLD_STAGE,
    API_HEAT_STAGE,
    API_NAME,
    API_ON,
    API_SET_POINT,
]

AZD_AIR_DEMAND = "air_demand"
AZD_COLD_STAGE = "cold_stage"
AZD_COLD_STAGES = "cold_stages"
AZD_DEMAND = "demand"
AZD_ERRORS = "errors"
AZD_FLOOR_DEMAND = "floor_demand"
AZD_HEAT_STAGE = "heat_stage"
AZD_HEAT_STAGES = "heat_stages"
AZD_HUMIDITY = "humidity"
AZD_ID = "id"
AZD_MASTER = "master"
AZD_MODE = "mode"
AZD_MODES = "modes"
AZD_NAME = "name"
AZD_ON = "on"
AZD_PROBLEMS = "problems"
AZD_SYSTEM = "system"
AZD_SYSTEMS = "systems"
AZD_SYSTEMS_NUM = "num_systems"
AZD_TEMP = "temp"
AZD_TEMP_MAX = "temp_max"
AZD_TEMP_MIN = "temp_min"
AZD_TEMP_SET = "temp_set"
AZD_TEMP_UNIT = "temp_unit"
AZD_ZONES = "zones"
AZD_ZONES_NUM = "num_zones"

HTTP_CALL_TIMEOUT = 10
