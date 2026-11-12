"""Airzone Local API Entity."""

from __future__ import annotations

import logging
from typing import Any

from .common import EntityType

_LOGGER = logging.getLogger(__name__)


class Entity:
    """Airzone Entity."""

    def __init__(
        self,
        entity_type: EntityType,
        system_id: int | None = None,
        device_id: int | None = None,
    ):
        """Entity init."""
        entity_id = entity_type.type_str()
        if system_id is not None:
            entity_id += f"_{system_id}"
        if device_id is not None:
            entity_id += f"_{device_id}"
        self.entity_id = entity_id

    def get_entity_id(self) -> str:
        """Return Entity ID."""
        return self.entity_id

    def update_mqtt(self, data: dict[str, Any]) -> None:
        """Perform Entity MQTT update."""
        _LOGGER.debug("update_mqtt: entity_id=%s data=%s", self.entity_id, data)
