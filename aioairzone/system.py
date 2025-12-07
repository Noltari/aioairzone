"""Airzone Local API Device."""

from __future__ import annotations

import logging
from typing import Any

from .common import EcoAdapt, QAdapt, SystemType, parse_bool, parse_int, parse_str
from .const import (
    API_ECO_ADAPT,
    API_ERRORS,
    API_MANUFACTURER,
    API_MC_CONNECTED,
    API_POWER,
    API_Q_ADAPT,
    API_SYSTEM_FIRMWARE,
    API_SYSTEM_TYPE,
    API_ZONE_ID,
    AZD_AVAILABLE,
    AZD_CLAMP_METER,
    AZD_ECO_ADAPT,
    AZD_ENERGY,
    AZD_ERRORS,
    AZD_FIRMWARE,
    AZD_FULL_NAME,
    AZD_ID,
    AZD_MANUFACTURER,
    AZD_MASTERS,
    AZD_MASTERS_SLAVES,
    AZD_MODEL,
    AZD_PROBLEMS,
    AZD_Q_ADAPT,
    AZD_SLAVES,
    ERROR_SYSTEM,
)
from .zone import Zone

_LOGGER = logging.getLogger(__name__)


class System:
    """Airzone System."""

    def __init__(self, system_id: int, zone_data: dict[str, Any]):
        """System init."""
        self.available: bool = True
        self.clamp_meter: bool | None = None
        self.eco_adapt: EcoAdapt | None = None
        self.energy: int | None = None
        self.errors: dict[int, list[str]] = {}
        self.id: int = system_id
        self.firmware: str | None = None
        self.manufacturer: str | None = None
        self.masters: dict[int, Zone] = {}
        self.q_adapt: QAdapt | None = None
        self.slaves: dict[int, Zone] = {}
        self.type: SystemType | None = None
        self.zones: dict[int, Zone] = {}

        self.update_zone_data(zone_data)

    def update_zone_data(self, zone_data: dict[str, Any]) -> None:
        """Update System data."""
        self.available = True

        zone_id = int(zone_data.get(API_ZONE_ID, 0))
        errors: list[dict[str, str]] | None = zone_data.get(API_ERRORS)
        if errors is not None and zone_id > 0:
            self.errors[zone_id] = []
            for error in errors:
                for key, val in error.items():
                    self.add_error(zone_id, val, key)

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

        masters = self.get_masters()
        if masters is not None:
            data[AZD_MASTERS] = masters

        masters_slaves = self.get_masters_slaves()
        if masters_slaves is not None:
            data[AZD_MASTERS_SLAVES] = masters_slaves

        model = self.get_model()
        if model is not None:
            data[AZD_MODEL] = model

        data[AZD_PROBLEMS] = self.get_problems()

        q_adapt = self.get_qadapt()
        if q_adapt is not None:
            data[AZD_Q_ADAPT] = q_adapt

        slaves = self.get_slaves()
        if slaves is not None:
            data[AZD_SLAVES] = slaves

        return data

    def add_error(self, zone_id: int, error: str, error_id: str | None = None) -> None:
        """Add system error."""
        if error_id is not None:
            if (
                error_id.casefold() == ERROR_SYSTEM
                and error not in self.errors[zone_id]
            ):
                self.errors[zone_id] += [error]
        else:
            if error not in self.errors[zone_id]:
                self.errors[zone_id] += [error]

    def add_zone(self, zone: Zone) -> None:
        """Add zone to system."""
        zone_id = zone.get_id()
        if zone_id not in self.zones:
            self.zones[zone_id] = zone
        if zone.get_master():
            if zone_id not in self.masters:
                self.masters[zone_id] = zone
            if zone_id in self.slaves:
                self.slaves.pop(zone_id)
        else:
            if zone_id not in self.slaves:
                self.slaves[zone_id] = zone
            if zone_id in self.masters:
                self.masters.pop(zone_id)

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
        errors: list[str] = []
        for zone_errors in self.errors.values():
            errors += zone_errors
        return errors

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

    def get_masters(self) -> list[int] | None:
        """Return system master zones."""
        if len(self.masters) > 0:
            return list(self.masters.keys())
        return None

    def get_masters_slaves(self) -> dict[int, list[int]] | None:
        """Return system masters and slaves zones."""
        if len(self.masters) == 0:
            return None
        masters: dict[int, list[int]] = {}
        for master in self.masters.values():
            master_id = master.get_id()
            masters[master_id] = []
            for slave in self.slaves.values():
                slave_master = slave.get_master_zone()
                if slave_master is None or slave_master == master_id:
                    masters[master_id] += [slave.get_id()]
        return masters

    def get_model(self) -> str | None:
        """Return system model."""
        if self.type:
            return str(self.type)
        return None

    def get_problems(self) -> bool:
        """Return system problems."""
        for zone_errors in self.errors.values():
            if len(zone_errors) > 0:
                return True
        return False

    def get_qadapt(self) -> QAdapt | None:
        """Return system Q-Adapt."""
        return self.q_adapt

    def get_slave_master(self, slave: Zone) -> Zone | None:
        """Find the corresponding master from a slave."""
        master_id = slave.get_master_zone()
        if master_id is None:
            if len(self.masters) > 0:
                master = list(self.masters.values())[0]
            else:
                master = None
            if len(self.masters) > 1:
                _LOGGER.warning(
                    "multiple masters for %s -> %s",
                    slave.get_system_zone_id(),
                    list(self.masters.keys()),
                )
        else:
            master = self.masters.get(master_id)
        return master

    def get_slaves(self) -> list[int] | None:
        """Return system slave zones."""
        if len(self.slaves) > 0:
            return list(self.slaves.keys())
        return None

    def set_available(self, available: bool) -> None:
        """Set availability."""
        self.available = available

    def set_eco_adapt(self, eco_adapt: EcoAdapt | None) -> None:
        """Set system Eco Adapt."""
        self.eco_adapt = eco_adapt

    def set_master_param(self, master: int | None, key: str, value: Any) -> None:
        """Update master parameter by key and value."""
        if master is None or master == 0:
            self.set_param_all_zones(key, value)
        else:
            self.set_param_master_zone(master, key, value)

    def set_param(self, key: str, value: Any) -> None:
        """Update parameter by key and value."""
        if key == API_ECO_ADAPT:
            self.eco_adapt = EcoAdapt(value)
        elif key == API_Q_ADAPT:
            self.q_adapt = QAdapt(value)

    def set_param_all_zones(self, key: str, value: Any) -> None:
        """Update all zones parameter by key and value."""
        for zone in self.zones.values():
            zone.set_param(key, value)

    def set_param_master_zone(self, master: int | None, key: str, value: Any) -> None:
        """Update master zone parameter by key and value."""
        for zone in self.zones.values():
            if zone.get_master():
                if zone.get_id() == master:
                    zone.set_param(key, value)
            else:
                if zone.get_master_zone() == master:
                    zone.set_param(key, value)

    def update_data(self, data: dict[str, Any]) -> None:
        """Update system parameters by dict."""

        self.available = True

        mc_connected = parse_bool(data.get(API_MC_CONNECTED))
        if mc_connected is not None:
            self.clamp_meter = mc_connected

        errors: list[dict[str, str]] | None = data.get(API_ERRORS)
        if errors is not None:
            self.errors[0] = []
            for error in errors:
                for val in error.values():
                    self.add_error(0, val)

        manufacturer = parse_str(data.get(API_MANUFACTURER))
        if manufacturer is not None:
            self.manufacturer = manufacturer

        power = parse_int(data.get(API_POWER))
        if power is not None:
            self.energy = power

        system_firmware = parse_str(data.get(API_SYSTEM_FIRMWARE))
        if system_firmware is not None:
            self.firmware = system_firmware

        system_type = parse_int(data.get(API_SYSTEM_TYPE))
        if system_type is not None:
            self.type = SystemType(system_type)

        q_adapt = parse_int(data.get(API_Q_ADAPT))
        if q_adapt is not None:
            self.q_adapt = QAdapt(q_adapt)
