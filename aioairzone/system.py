"""Airzone Local API Device."""

from __future__ import annotations

from typing import Any

from .common import EcoAdapt, OperationMode, SystemType
from .const import (
    API_ECO_ADAPT,
    API_ERRORS,
    API_MANUFACTURER,
    API_MC_CONNECTED,
    API_MODE,
    API_POWER,
    API_SYSTEM_FIRMWARE,
    API_SYSTEM_TYPE,
    AZD_AVAILABLE,
    AZD_CLAMP_METER,
    AZD_ECO_ADAPT,
    AZD_ENERGY,
    AZD_ERRORS,
    AZD_FIRMWARE,
    AZD_FULL_NAME,
    AZD_ID,
    AZD_MANUFACTURER,
    AZD_MASTER_SYSTEM_ZONE,
    AZD_MASTER_ZONE,
    AZD_MODE,
    AZD_MODEL,
    AZD_MODES,
    AZD_PROBLEMS,
    ERROR_SYSTEM,
)
from .zone import Zone


class System:
    """Airzone System."""

    def __init__(self, system_id: int, zone_data: dict[str, Any]):
        """System init."""
        self.available: bool = True
        self.clamp_meter: bool | None = None
        self.eco_adapt: EcoAdapt | None = None
        self.energy: int | None = None
        self.errors: list[str] = []
        self.id: int = system_id
        self.firmware: str | None = None
        self.manufacturer: str | None = None
        self.master_system_zone: str | None = None
        self.master_zone: int | None = None
        self.mode: OperationMode | None = None
        self.modes: list[OperationMode] = []
        self.type: SystemType | None = None
        self.zones: dict[int, Zone] = {}

        self.update_zone_data(zone_data)

    def update_zone_data(self, zone_data: dict[str, Any]) -> None:
        """Update System data."""
        self.available = True

        errors: list[dict[str, str]] = zone_data.get(API_ERRORS, [])
        for error in errors:
            for key, val in error.items():
                self.add_error(val, key)

    def data(self) -> dict[str, Any]:
        """Return Airzone system data."""
        data: dict[str, Any] = {}

        data[AZD_AVAILABLE] = self.get_available()

        clamp_meter = self.get_clamp_meter()
        if clamp_meter is not None:
            data[AZD_CLAMP_METER] = clamp_meter

            if clamp_meter:
                energy = self.get_energy()
                if energy is not None:
                    data[AZD_ENERGY] = energy

        eco_adapt = self.get_eco_adapt()
        if eco_adapt is not None:
            data[AZD_ECO_ADAPT] = eco_adapt

        errors = self.get_errors()
        if len(errors) > 0:
            data[AZD_ERRORS] = errors

        firmware = self.get_firmware()
        if firmware is not None:
            data[AZD_FIRMWARE] = firmware

        full_name = self.get_full_name()
        if full_name is not None:
            data[AZD_FULL_NAME] = full_name

        data[AZD_ID] = self.get_id()

        manufacturer = self.get_manufacturer()
        if manufacturer is not None:
            data[AZD_MANUFACTURER] = manufacturer

        master_system_zone = self.get_master_system_zone()
        if master_system_zone is not None:
            data[AZD_MASTER_SYSTEM_ZONE] = master_system_zone

        master_zone = self.get_master_zone()
        if master_zone is not None:
            data[AZD_MASTER_ZONE] = master_zone

        mode = self.get_mode()
        if mode is not None:
            data[AZD_MODE] = mode

        model = self.get_model()
        if self.type is not None:
            data[AZD_MODEL] = model

        modes = self.get_modes()
        if modes is not None:
            data[AZD_MODES] = modes

        data[AZD_PROBLEMS] = self.get_problems()

        return data

    def add_error(self, error: str, error_id: str | None = None) -> None:
        """Add system error."""
        if error_id is not None:
            if error_id.casefold() == ERROR_SYSTEM and error not in self.errors:
                self.errors += [error]
        else:
            if error not in self.errors:
                self.errors += [error]

    def add_zone(self, zone: Zone) -> None:
        """Add zone to system."""
        zone_id = zone.get_id()
        if zone_id not in self.zones:
            self.zones[zone_id] = zone

    def get_available(self) -> bool:
        """Return availability."""
        return self.available

    def get_clamp_meter(self) -> bool | None:
        """Return system clamp meter connection."""
        return self.clamp_meter

    def get_eco_adapt(self) -> EcoAdapt | None:
        """Return system Eco Adapt."""
        return self.eco_adapt

    def get_energy(self) -> int | None:
        """Return system energy consumption."""
        return self.energy

    def get_errors(self) -> list[str]:
        """Return system errors."""
        return self.errors

    def get_id(self) -> int:
        """Return system ID."""
        return self.id

    def get_firmware(self) -> str | None:
        """Return system firmware."""
        if self.firmware and "." not in self.firmware and len(self.firmware) > 2:
            return f"{self.firmware[0:1]}.{self.firmware[1:]}"
        return self.firmware

    def get_full_name(self) -> str:
        """Return full name."""
        return f"Airzone [{self.get_id()}] System"

    def get_manufacturer(self) -> str | None:
        """Return system manufacturer."""
        return self.manufacturer

    def get_master_system_zone(self) -> str | None:
        """Return master system zone ID."""
        return self.master_system_zone

    def get_master_zone(self) -> int | None:
        """Return master zone ID."""
        return self.master_zone

    def get_model(self) -> str | None:
        """Return system model."""
        if self.type:
            return str(self.type)
        return None

    def get_mode(self) -> OperationMode | None:
        """Return system mode."""
        return self.mode

    def get_modes(self) -> list[OperationMode]:
        """Return system modes."""
        modes = self.modes

        if len(modes) == 0 and self.mode is not None:
            modes = [self.mode]

        if OperationMode.STOP not in modes:
            modes += [OperationMode.STOP]

        return modes

    def get_problems(self) -> bool:
        """Return system problems."""
        return bool(self.errors)

    def set_available(self, available: bool) -> None:
        """Set availability."""
        self.available = available

    def set_eco_adapt(self, eco_adapt: EcoAdapt | None) -> None:
        """Set system Eco Adapt."""
        self.eco_adapt = eco_adapt

    def set_master_system_zone(self, master_system_zone: str) -> None:
        """Set master system zone ID."""
        self.master_system_zone = master_system_zone

    def set_master_zone(self, master_zone: int) -> None:
        """Set master zone ID."""
        self.master_zone = master_zone

    def set_mode(self, mode: OperationMode | None) -> None:
        """Set system mode."""
        self.mode = mode

    def set_modes(self, modes: list[OperationMode]) -> None:
        """Set system modes."""
        self.modes = modes

    def set_param(self, key: str, value: Any) -> None:
        """Update parameters by key and value."""
        if key == API_ECO_ADAPT:
            self.eco_adapt = EcoAdapt(value)
        elif key == API_MODE:
            self.mode = OperationMode(value)

        for zone in self.zones.values():
            zone.set_param(key, value)

    def update_data(self, data: dict[str, Any]) -> None:
        """Update system parameters by dict."""

        self.available = True

        if API_MC_CONNECTED in data:
            self.clamp_meter = bool(data[API_MC_CONNECTED])

        if API_ERRORS in data:
            errors: list[dict[str, str]] = data[API_ERRORS]
            for error in errors:
                for val in error.values():
                    self.add_error(val)

        if API_MANUFACTURER in data:
            self.manufacturer = str(data[API_MANUFACTURER])

        if API_POWER in data:
            self.energy = int(data[API_POWER])

        if API_SYSTEM_FIRMWARE in data:
            self.firmware = str(data[API_SYSTEM_FIRMWARE])

        if API_SYSTEM_TYPE in data:
            self.type = SystemType(data[API_SYSTEM_TYPE])
