"""Sensor entities for Eigen SmartLife."""

from __future__ import annotations

import json
from typing import Any

from tuya_sharing import CustomerDevice, Manager

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EigenRuntime
from .devices import DeviceProfile, EntityProfile, get_profile
from .entity import EigenEntity


def _sensor_metadata(device: CustomerDevice, profile: EntityProfile) -> dict[str, Any]:
    metadata: dict[str, Any] = {"unit": profile.unit, "scale": 0}
    status_range = getattr(device, "status_range", {})
    specification = (
        status_range.get(profile.code) if isinstance(status_range, dict) else None
    )
    values = getattr(specification, "values", None)
    if not values:
        return metadata

    try:
        parsed = json.loads(values) if isinstance(values, str) else values
    except (TypeError, json.JSONDecodeError):
        return metadata
    if not isinstance(parsed, dict):
        return metadata

    if parsed.get("unit"):
        metadata["unit"] = parsed["unit"]
    if isinstance(parsed.get("scale"), int):
        metadata["scale"] = parsed["scale"]
    return metadata


class EigenSensor(EigenEntity, SensorEntity):
    """Read-only numeric Tuya DP."""

    def __init__(
        self,
        device: CustomerDevice,
        manager: Manager,
        device_profile: DeviceProfile,
        entity_profile: EntityProfile,
    ) -> None:
        super().__init__(device, manager, device_profile, entity_profile)
        metadata = _sensor_metadata(device, entity_profile)
        self._scale = int(metadata["scale"])
        self._attr_native_unit_of_measurement = metadata["unit"]
        self._attr_device_class = entity_profile.device_class
        self._attr_state_class = entity_profile.state_class

    @property
    def native_value(self) -> float | int | None:
        value = self._status()
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if self._scale <= 0:
            return value
        return value / (10**self._scale)


def _entities_for_device(
    device: CustomerDevice, manager: Manager, profile: DeviceProfile
) -> list[EigenSensor]:
    entities: list[EigenSensor] = []
    status = getattr(device, "status", {})
    for definition in profile.entities:
        if definition.platform is not Platform.SENSOR:
            continue
        if definition.code not in status:
            continue
        entities.append(EigenSensor(device, manager, profile, definition))
    return entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Eigen sensors."""
    runtime: EigenRuntime = entry.runtime_data
    manager = runtime.manager
    if manager is None:
        return

    entities: list[EigenSensor] = []
    for device in manager.device_map.values():
        profile = get_profile(getattr(device, "product_id", None))
        if profile is None or profile.discovery_only:
            continue
        entities.extend(_entities_for_device(device, manager, profile))

    async_add_entities(entities)
