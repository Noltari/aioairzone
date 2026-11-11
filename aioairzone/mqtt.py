"""Airzone MQTT."""

from enum import Enum, auto
import json
from json import JSONDecodeError
import logging
from typing import Any

from .common import EntityType
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

_LOGGER = logging.getLogger(__name__)


class AirzoneMqttUpdateType(Enum):
    """Airzone stages."""

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
        payload: bytes | bytearray,
    ):
        """Airzone MQTT update init."""
        self.topic = topic
        self.topics = topic.split("/")

        try:
            self.data = json.loads(payload)
        except JSONDecodeError as err:
            self.data = {}
            _LOGGER.error(err)

        self.device_id = None
        self.entity_id = None
        self.entity_type = None
        self.system_id = None
        self.type = AirzoneMqttUpdateType.Unknown

        if self.topics[0] == MQTT_TOPIC_V1:
            self.version = self.topics[0]
            self.parse_v1(self.topics[1:])
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

    def parse_entity_type(self, entity_type: str) -> None:
        """Airzone MQTT parse entity type."""
        if entity_type in MQTT_DEV_TYPES_HOT_WATER:
            self.entity_type = EntityType.HotWater
        elif entity_type in MQTT_DEV_TYPES_SYSTEM:
            self.entity_type = EntityType.System
        elif entity_type in MQTT_DEV_TYPES_ZONE:
            self.entity_type = EntityType.Zone
        else:
            self.entity_type = EntityType.Unknown

    def parse_v1(self, topics: list[str]) -> None:
        """Airzone MQTT parse v1."""
        if topics[0] == MQTT_TOPIC_ONLINE:
            self.type = AirzoneMqttUpdateType.Online
        elif topics[0] == MQTT_TOPIC_EVENTS and topics[1] == MQTT_TOPIC_STATUS:
            self.type = AirzoneMqttUpdateType.EventsStatus

            self.parse_entity_type(topics[2])
            self.system_id = int(topics[3])
            self.device_id = int(topics[4])

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
