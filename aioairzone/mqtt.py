"""Airzone MQTT."""

from enum import Enum, IntEnum, auto
from typing import Any

from .const import (
    AZD_ONLINE,
    MQTT_API_ONLINE,
    MQTT_TOPIC_EVENTS,
    MQTT_TOPIC_INVOKE,
    MQTT_TOPIC_ONLINE,
    MQTT_TOPIC_STATUS,
    MQTT_TOPIC_V1,
)


class AirzoneMqttTopic(IntEnum):
    """Airzone MQTT topic."""

    Version = 0
    ReqType = 1
    ReqSubType = 2


class AirzoneMqttUpdateType(Enum):
    """Airzone MQTT update type."""

    EventsStatus = auto()
    Invoke = auto()
    Online = auto()
    Unknown = auto()


class AirzoneMqttUpdate:
    """Airzone MQTT update."""

    data: dict[str, Any]
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
        self.type = AirzoneMqttUpdateType.Unknown

        version = self.get_topic_index(AirzoneMqttTopic.Version)
        if version == MQTT_TOPIC_V1:
            self.version = version
            self.parse_v1()
        else:
            self.version = None

    def get_topic_index(self, index: int, default: str | None = None) -> str | None:
        """Airzone MQTT topic by index."""
        try:
            return self.topics[index]
        except IndexError:
            return default

    def parse_v1(self) -> None:
        """Airzone MQTT parse v1."""
        req_type = self.get_topic_index(AirzoneMqttTopic.ReqType)
        req_subtype = self.get_topic_index(AirzoneMqttTopic.ReqSubType)
        if req_type == MQTT_TOPIC_ONLINE:
            self.type = AirzoneMqttUpdateType.Online
        elif req_type == MQTT_TOPIC_EVENTS and req_subtype == MQTT_TOPIC_STATUS:
            self.type = AirzoneMqttUpdateType.EventsStatus
        elif req_type == MQTT_TOPIC_INVOKE:
            self.type = AirzoneMqttUpdateType.Invoke
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
