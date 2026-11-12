"""Airzone MQTT."""

from enum import Enum, IntEnum, auto
from typing import Any

from .common import EntityType, parse_int
from .const import (
    AZD_ONLINE,
    MQTT_API_ONLINE,
    MQTT_DEV_TYPES_HOT_WATER,
    MQTT_DEV_TYPES_SYSTEM,
    MQTT_DEV_TYPES_ZONE,
    MQTT_TOPIC_EVENTS,
    MQTT_TOPIC_ONLINE,
    MQTT_TOPIC_STATUS,
    MQTT_TOPIC_V1,
)


class AirzoneMqttTopic(IntEnum):
    """Airzone MQTT topic."""

    Version = 0
    ReqType = 1
    ReqSubType = 2
    DevType = 3
    SysID = 4
    DevID = 5


class AirzoneMqttUpdateType(Enum):
    """Airzone MQTT update type."""

    EventsStatus = auto()
    Online = auto()
    Unknown = auto()


class AirzoneMqttUpdate:
    """Airzone MQTT update."""

    data: dict[str, Any]
    device_id: int | None
    entity_id: str | None
    entity_type: EntityType | None
    system_id: int | None
    topic: str
    topics: list[str]
    type: AirzoneMqttUpdateType
    version: str | None

    def __init__(
        self,
        topic: str,
        data: dict[str, Any],
    ):
        """Airzone MQTT update init."""
        self.data = data
        self.topic = topic
        self.topics = topic.split("/")

        self.device_id = None
        self.entity_id = None
        self.entity_type = None
        self.system_id = None
        self.type = AirzoneMqttUpdateType.Unknown

        version = self.get_topic_index(AirzoneMqttTopic.Version)
        if version == MQTT_TOPIC_V1:
            self.version = version
            self.parse_v1()
        else:
            self.version = None

    def build_entity_id(self) -> None:
        """Airzone MQTT parse device type."""
        if self.entity_type is not None:
            entity_id = self.entity_type.type_str()
            if self.system_id is not None:
                entity_id += f"_{self.system_id}"
            if self.device_id is not None:
                entity_id += f"_{self.device_id}"
            self.entity_id = entity_id

    def get_topic_index(self, index: int, default: str | None = None) -> str | None:
        """Airzone MQTT topic by index."""
        try:
            return self.topics[index]
        except IndexError:
            return default

    def parse_device_type(self, device_type: str | None) -> EntityType:
        """Airzone MQTT parse device type."""
        if device_type in MQTT_DEV_TYPES_HOT_WATER:
            entity_type = EntityType.HotWater
        elif device_type in MQTT_DEV_TYPES_SYSTEM:
            entity_type = EntityType.System
        elif device_type in MQTT_DEV_TYPES_ZONE:
            entity_type = EntityType.Zone
        else:
            entity_type = EntityType.Unknown
        return entity_type

    def parse_v1(self) -> None:
        """Airzone MQTT parse v1."""
        req_type = self.get_topic_index(AirzoneMqttTopic.ReqType)
        req_subtype = self.get_topic_index(AirzoneMqttTopic.ReqSubType)
        if req_type == MQTT_TOPIC_ONLINE:
            self.type = AirzoneMqttUpdateType.Online
        elif req_type == MQTT_TOPIC_EVENTS and req_subtype == MQTT_TOPIC_STATUS:
            self.type = AirzoneMqttUpdateType.EventsStatus

            device_type = self.get_topic_index(AirzoneMqttTopic.DevType)
            entity_type = self.parse_device_type(device_type)
            if entity_type != EntityType.Unknown:
                self.entity_type = entity_type

            system_id = parse_int(self.get_topic_index(AirzoneMqttTopic.SysID))
            if system_id is not None and system_id > 0:
                self.system_id = system_id

            device_id = parse_int(self.get_topic_index(AirzoneMqttTopic.DevID))
            if device_id is not None and device_id > 0:
                self.device_id = device_id

            self.build_entity_id()
        else:
            self.type = AirzoneMqttUpdateType.Unknown


class AirzoneMqtt:
    """Airzone MQTT."""

    def __init__(self) -> None:
        """Airzone MQTT init."""
        self.online: bool = False

    def update_online(self, update: AirzoneMqttUpdate) -> None:
        """Perform MQTT online."""
        data = update.data

        online = data.get(MQTT_API_ONLINE)
        if online is not None:
            self.online = bool(online)

    def get_online(self) -> bool:
        """Return MQTT online."""
        return self.online

    def data(self) -> dict[str, Any]:
        """Return Airzone MQTT data."""
        data: dict[str, Any] = {
            AZD_ONLINE: self.get_online(),
        }

        return data
