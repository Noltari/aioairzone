"""Airzone Local API HVAC."""

from enum import IntEnum
import random
from typing import Any, cast

from aiohttp import web
from aiohttp.web_response import Response
from helpers import (
    api_filter_dict,
    api_json_error,
    api_json_response,
    celsius_to_fahrenheit,
)

from aioairzone.common import (
    OperationMode,
    SystemType,
    TemperatureUnit,
    get_system_zone_id,
)
from aioairzone.const import (
    API_ACS_MAX_TEMP,
    API_ACS_MIN_TEMP,
    API_ACS_ON,
    API_ACS_POWER_MODE,
    API_ACS_SET_POINT,
    API_ACS_TEMP,
    API_COOL_MAX_TEMP,
    API_COOL_MIN_TEMP,
    API_COOL_SET_POINT,
    API_DATA,
    API_DOUBLE_SET_POINT,
    API_ERROR_HOT_WATER_NOT_CONNECTED,
    API_ERROR_REQUEST_MALFORMED,
    API_ERROR_SYSTEM_ID_NOT_AVAILABLE,
    API_ERROR_SYSTEM_ID_NOT_PROVIDED,
    API_ERROR_SYSTEM_ID_OUT_RANGE,
    API_ERROR_ZONE_ID_NOT_AVAILABLE,
    API_ERRORS,
    API_HEAT_MAX_TEMP,
    API_HEAT_MIN_TEMP,
    API_HEAT_SET_POINT,
    API_HUMIDITY,
    API_MANUFACTURER,
    API_MAX_TEMP,
    API_MC_CONNECTED,
    API_MIN_TEMP,
    API_MODE,
    API_MODES,
    API_NAME,
    API_ON,
    API_POWER,
    API_ROOM_TEMP,
    API_SET_POINT,
    API_SYSTEM_FIRMWARE,
    API_SYSTEM_ID,
    API_SYSTEM_TYPE,
    API_SYSTEMS,
    API_UNITS,
    API_ZONE_ID,
)


class AirzoneACSStatus(IntEnum):
    """Supported features of the Airzone Local API."""

    ENABLED = 0
    DISABLED = 1
    BOGUS = 2


class AirzoneACS:
    """Airzone Local API ACS."""

    def __init__(self) -> None:
        """Local API ACS init."""
        self.id: int = 0
        self.on: bool = True
        self.power: bool = False
        self.status: AirzoneACSStatus = AirzoneACSStatus.DISABLED
        self.temp: int = 40
        self.temp_max: int = 65
        self.temp_min: int = 25
        self.temp_set: int = 45

    def data(self) -> dict[str, Any]:
        """Return Local API ACS data."""
        if self.status == AirzoneACSStatus.BOGUS:
            return {
                API_ACS_MAX_TEMP: 0,
                API_ACS_MIN_TEMP: 0,
                API_ACS_ON: 0,
                API_ACS_POWER_MODE: 0,
                API_ACS_SET_POINT: 0,
                API_ACS_TEMP: 0,
                API_SYSTEM_ID: 0,
            }

        return {
            API_ACS_MAX_TEMP: self.temp_max,
            API_ACS_MIN_TEMP: self.temp_min,
            API_ACS_ON: int(self.on),
            API_ACS_POWER_MODE: int(self.power),
            API_ACS_SET_POINT: self.temp_set,
            API_ACS_TEMP: self.temp,
            API_SYSTEM_ID: self.id,
        }

    def refresh(self) -> None:
        """Refresh Local API ACS."""
        if self.status != AirzoneACSStatus.ENABLED:
            return

        temp = self.temp_set + (random.randrange(-100, 100, 1) / 10)
        if temp <= self.temp_min:
            temp = self.temp_min
        elif temp >= self.temp_max:
            temp = self.temp_max
        self.temp = int(temp)

    def set_status(self, status: AirzoneACSStatus) -> None:
        """Set Airzone ACS status."""
        self.status = status

    async def post(self) -> Response:
        """POST Local API ACS."""
        if self.status == AirzoneACSStatus.DISABLED:
            return api_json_error(API_ERROR_HOT_WATER_NOT_CONNECTED)

        self.refresh()
        return api_json_response(self.data())

    async def put(self, data: dict[str, Any]) -> Response:
        """PUT Local API ACS."""
        if self.status == AirzoneACSStatus.DISABLED:
            return api_json_error(API_ERROR_HOT_WATER_NOT_CONNECTED)

        keys = list(data) + [API_SYSTEM_ID]

        on = data.get(API_ACS_ON)
        if on is not None:
            self.on = bool(on)

        power = data.get(API_ACS_POWER_MODE)
        if power is not None:
            self.power = bool(power)

        temp_set = data.get(API_ACS_SET_POINT)
        if temp_set is not None:
            self.temp_set = int(temp_set)

        return api_json_response(api_filter_dict(self.data(), keys))


class AirzoneSystem:
    """Airzone Local API System."""

    def __init__(self, system_id: int):
        """Local API System init."""
        self.errors: list[dict[str, str]] = []
        self.firmware: str = "3.36"
        self.id: int = system_id
        self.mc_connected: bool = False
        self.manufacturer: str = "Python"
        self.power: int = 0
        self.type: SystemType = SystemType.C3

    def data(self) -> dict[str, Any]:
        """Return Local API System data."""
        return {
            API_ERRORS: self.errors,
            API_MANUFACTURER: self.manufacturer,
            API_MC_CONNECTED: int(self.mc_connected),
            API_POWER: self.power,
            API_SYSTEM_FIRMWARE: self.firmware,
            API_SYSTEM_ID: self.id,
            API_SYSTEM_TYPE: self.type.value,
        }

    def matches(self, system_id: int) -> bool:
        """Check if system matches param."""
        matches = False
        if system_id in (0, 127, self.id):
            matches = True
        return matches

    def refresh(self) -> None:
        """Refresh Local API System."""
        if self.mc_connected:
            self.power = random.randrange(0, 5, 1)

    def post(self) -> dict[str, Any]:
        """POST Local API System."""
        self.refresh()
        return self.data()

    def put(self) -> dict[str, Any]:
        """PUT Local API System."""
        return self.data()


class AirzoneZone:
    """Airzone Local API Zone."""

    def __init__(self, name: str, system_id: int, zone_id: int, units: TemperatureUnit):
        """Local API Zone init."""
        self.cool_temp_set: float = 22
        self.cool_temp_max: float = 30
        self.cool_temp_min: float = 18
        self.heat_temp_set: float = 21
        self.heat_temp_max: float = 30
        self.heat_temp_min: float = 15
        self.errors: list[dict[str, str]] = []
        self.humidity: int = 50
        self.id: int = zone_id
        self.mode: OperationMode = OperationMode.HEATING
        self.modes: list[OperationMode] = [
            OperationMode.COOLING,
            OperationMode.HEATING,
            OperationMode.AUTO,
        ]
        self.name: str = name
        self.on: bool = True
        self.system: int = system_id
        self.temp: float = 22.3
        self.temp_max: float = 30
        self.temp_min: float = 15
        self.temp_set: float = 21
        self.units: TemperatureUnit = units

    def conv_temp(self, temp: float | int) -> float | int:
        """Convert temperature to Fahrenheit if needed."""
        if self.units == TemperatureUnit.FAHRENHEIT:
            return celsius_to_fahrenheit(temp)
        return temp

    def get_modes(self) -> list[int]:
        """Get list of modes as integers."""
        modes: list[int] = []
        for mode in self.modes:
            modes += [int(mode)]
        return modes

    def data(self) -> dict[str, Any]:
        """Return Local API Zone data."""
        _data: dict[str, Any] = {
            API_COOL_SET_POINT: self.conv_temp(self.cool_temp_set),
            API_COOL_MAX_TEMP: self.conv_temp(self.cool_temp_max),
            API_COOL_MIN_TEMP: self.conv_temp(self.cool_temp_min),
            API_ERRORS: self.errors,
            API_HEAT_SET_POINT: self.conv_temp(self.heat_temp_set),
            API_HEAT_MAX_TEMP: self.conv_temp(self.heat_temp_max),
            API_HEAT_MIN_TEMP: self.conv_temp(self.heat_temp_min),
            API_HUMIDITY: self.humidity,
            API_MAX_TEMP: self.conv_temp(self.temp_max),
            API_MIN_TEMP: self.conv_temp(self.temp_min),
            API_MODE: self.mode,
            API_MODES: self.get_modes(),
            API_ON: int(self.on),
            API_ROOM_TEMP: self.conv_temp(self.temp),
            API_SET_POINT: self.conv_temp(self.temp_set),
            API_SYSTEM_ID: self.system,
            API_UNITS: int(self.units),
            API_ZONE_ID: self.id,
        }
        if len(self.name) > 0:
            _data[API_NAME] = self.name
        if OperationMode.AUTO in _data[API_MODES]:
            _data[API_DOUBLE_SET_POINT] = True
        return _data

    def matches(self, system_id: int, zone_id: int) -> bool:
        """Check if Zone matches params."""
        matches = False
        if system_id == 0:
            if zone_id == 0:
                matches = True
            elif zone_id == self.id:
                matches = True
        elif zone_id == 0:
            if system_id == self.system:
                matches = True
        elif system_id == self.system and zone_id == self.id:
            matches = True
        return matches

    def refresh(self) -> None:
        """Refresh Local API Zone."""
        self.humidity = 50 + random.randrange(-40, 40, 1)

        temp = self.temp_set + (random.randrange(-100, 100, 1) / 10)
        if temp <= self.temp_min:
            temp = self.temp_min
        elif temp >= self.temp_max:
            temp = self.temp_max
        self.temp = temp

    def post(self) -> dict[str, Any]:
        """POST Local API Zone."""
        self.refresh()
        return self.data()

    def put(self, data: dict[str, Any]) -> dict[str, Any]:
        """PUT Local API Zone."""
        keys = list(data) + [API_SYSTEM_ID, API_ZONE_ID]

        cool_temp_set = data.get(API_COOL_SET_POINT)
        if cool_temp_set is not None:
            self.cool_temp_set = self.conv_temp(float(cool_temp_set))

        heat_temp_set = data.get(API_HEAT_SET_POINT)
        if heat_temp_set is not None:
            self.heat_temp_set = self.conv_temp(float(heat_temp_set))

        mode = data.get(API_MODE)
        if mode is not None:
            self.mode = OperationMode(mode)

        on = data.get(API_ON)
        if on is not None:
            self.on = bool(on)

        temp_set = data.get(API_SET_POINT)
        if temp_set is not None:
            temp_set = float(temp_set)
            conv_temp_set = self.conv_temp(temp_set)
            self.temp_set = conv_temp_set
            if self.mode == OperationMode.AUTO:
                if temp_set >= self.temp:
                    self.heat_temp_set = conv_temp_set
                else:
                    self.cool_temp_set = conv_temp_set
            elif self.mode == OperationMode.COOLING:
                self.cool_temp_set = conv_temp_set
            elif self.mode == OperationMode.HEATING:
                self.heat_temp_set = conv_temp_set

        return cast(dict[str, Any], api_filter_dict(self.data(), keys))


class AirzoneHVAC:
    """Airzone Local API HVAC."""

    def __init__(self) -> None:
        """Local API HVAC init."""
        self.acs: AirzoneACS = AirzoneACS()
        self.systems: dict[int, AirzoneSystem] = {}
        self.zones: dict[str, AirzoneZone] = {}

    def add_zone(
        self, name: str, system_id: int, zone_id: int, units: TemperatureUnit
    ) -> bool:
        """Local API HVAC add Zone."""
        system_zone_id = get_system_zone_id(system_id, zone_id)
        if system_zone_id not in self.zones:
            if system_id not in self.systems:
                system = AirzoneSystem(system_id)
                self.systems[system_id] = system

            zone = AirzoneZone(name, system_id, zone_id, units)
            self.zones[system_zone_id] = zone

            return True
        return False

    def check_system(self, system_id: int) -> bool:
        """Check if System exists."""
        for zone in self.zones.values():
            if system_id in (0, 127, zone.system):
                return True
        return False

    def check_zone(self, system_id: int, zone_id: int) -> bool:
        """Check if Zone exists."""
        for zone in self.zones.values():
            if system_id in (0, zone.system):
                if zone_id in (0, zone.id):
                    return True
        return False

    def system_response(
        self, system_id: int, hvac_data: list[dict[str, Any]]
    ) -> Response:
        """Return HVAC System data."""
        if len(hvac_data) == 0:
            if not self.check_system(system_id):
                return api_json_error(API_ERROR_SYSTEM_ID_NOT_AVAILABLE)
            return api_json_error(API_ERROR_REQUEST_MALFORMED)
        return api_json_response({API_DATA: hvac_data})

    def post_system(self, system_id: int) -> Response:
        """POST Local API HVAC System."""
        hvac_data: list[dict[str, Any]] = []
        for system in self.systems.values():
            if system.matches(system_id):
                hvac_data += [system.post()]
        return self.system_response(system_id, hvac_data)

    def put_system(self, system_id: int) -> Response:
        """PUT Local API HVAC Zone."""
        hvac_data: list[dict[str, Any]] = []
        for system in self.systems.values():
            if system.matches(system_id):
                hvac_data += [system.put()]
        return self.system_response(system_id, hvac_data)

    def zone_response(
        self, system_id: int, zone_id: int, hvac_data: list[dict[str, Any]]
    ) -> Response:
        """Return HVAC Zone data."""
        if len(hvac_data) == 0:
            if not self.check_system(system_id):
                return api_json_error(API_ERROR_SYSTEM_ID_NOT_AVAILABLE)
            if not self.check_zone(system_id, zone_id):
                return api_json_error(API_ERROR_ZONE_ID_NOT_AVAILABLE)
            return api_json_error(API_ERROR_REQUEST_MALFORMED)
        if system_id == 0:
            response = {
                API_SYSTEMS: [
                    {
                        API_DATA: hvac_data,
                    }
                ]
            }
        else:
            response = {
                API_DATA: hvac_data,
            }
        return api_json_response(response)

    def post_zone(self, system_id: int, zone_id: int) -> Response:
        """POST Local API HVAC Zone."""
        hvac_data: list[dict[str, Any]] = []
        for zone in self.zones.values():
            if zone.matches(system_id, zone_id):
                hvac_data += [zone.post()]
        return self.zone_response(system_id, zone_id, hvac_data)

    def put_zone(self, system_id: int, zone_id: int, data: dict[str, Any]) -> Response:
        """PUT Local API HVAC Zone."""
        hvac_data: list[dict[str, Any]] = []
        for zone in self.zones.values():
            if zone.matches(system_id, zone_id):
                hvac_data += [zone.put(data)]
        return self.zone_response(system_id, zone_id, hvac_data)

    async def post(self, request: web.Request) -> Response:
        # pylint: disable=too-many-return-statements
        """POST Local API HVAC."""
        data = await request.json()
        if isinstance(data, dict):
            system = data.get(API_SYSTEM_ID)
            zone = data.get(API_ZONE_ID)
        else:
            system = None
            zone = None

        if system is None:
            return api_json_error(API_ERROR_SYSTEM_ID_NOT_PROVIDED)

        if system == 127:
            return self.post_system(system)

        if system == 0:
            if zone is None:
                return await self.acs.post()
            if 0 <= zone <= 32:
                return self.post_zone(system, zone)
            return api_json_error(API_ERROR_ZONE_ID_NOT_AVAILABLE)

        if 0 < system <= 32:
            if zone is None:
                return self.post_system(system)
            return self.post_zone(system, zone)

        return api_json_error(API_ERROR_SYSTEM_ID_OUT_RANGE)

    async def put(self, request: web.Request) -> Response:
        # pylint: disable=too-many-return-statements
        """PUT Local API HVAC."""
        data = await request.json()
        if isinstance(data, dict):
            system = data.get(API_SYSTEM_ID)
            zone = data.get(API_ZONE_ID)
        else:
            system = None
            zone = None

        if system is None:
            return api_json_error(API_ERROR_SYSTEM_ID_NOT_PROVIDED)

        if system == 127:
            return self.put_system(system)

        if system == 0:
            if zone is None:
                return await self.acs.put(data)
            if 0 <= zone <= 32:
                return self.put_zone(system, zone, data)
            return api_json_error(API_ERROR_ZONE_ID_NOT_AVAILABLE)

        if 0 < system <= 32:
            if zone is None:
                return self.put_system(system)
            return self.put_zone(system, zone, data)

        return api_json_error(API_ERROR_SYSTEM_ID_OUT_RANGE)
