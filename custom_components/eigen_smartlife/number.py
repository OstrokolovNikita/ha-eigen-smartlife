"""Number entities for Eigen SmartLife."""

from __future__ import annotations

import json
from typing import Any

from tuya_sharing import CustomerDevice, Manager

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EigenRuntime
from .devices import DeviceProfile, EntityProfile, get_profile
from .entity import EigenEntity


def _number_metadata(device: CustomerDevice, profile: EntityProfile) -> dict[str, Any]:
    """Prefer the live Tuya specification and fall back to the verified profile."""
    metadata: dict[str, Any] = {
        "min": profile.minimum,
        "max": profile.maximum,
        "step": profile.step,
        "unit": profile.unit,
    }

    function = getattr(device, "function", {})
    specification = function.get(profile.code) if isinstance(function, dict) else None
    values = getattr(specification, "values", None)
    if not values:
        return metadata

    try:
        parsed = json.loads(values) if isinstance(values, str) else values
    except (TypeError, json.JSONDecodeError):
        return metadata
    if not isinstance(parsed, dict):
        return metadata

    # Tuya Integer metadata commonly uses min/max/step/unit/scale.
    for key in ("min", "max", "step", "unit"):
        if parsed.get(key) is not None:
            metadata[key] = parsed[key]

    scale = parsed.get("scale")
    if isinstance(scale, int) and scale > 0:
        divisor = 10**scale
        for key in ("min", "max", "step"):
            if isinstance(metadata[key], (int, float)):
                metadata[key] = metadata[key] / divisor

    return metadata


class EigenNumber(EigenEntity, NumberEntity):
    """Integer Tuya DP exposed as a Home Assistant number."""

    _attr_mode = NumberMode.SLIDER
    _attr_device_class = NumberDeviceClass.TEMPERATURE

    def __init__(
        self,
        device: CustomerDevice,
        manager: Manager,
        device_profile: DeviceProfile,
        entity_profile: EntityProfile,
    ) -> None:
        super().__init__(device, manager, device_profile, entity_profile)
        metadata = _number_metadata(device, entity_profile)
        self._attr_native_min_value = float(metadata["min"])
        self._attr_native_max_value = float(metadata["max"])
        self._attr_native_step = float(metadata["step"])
        self._attr_native_unit_of_measurement = metadata["unit"]

    @property
    def native_value(self) -> float | None:
        value = self._status()
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        # All currently verified Eigen temperature DPs are integer values.
        command_value: int | float = int(value) if value.is_integer() else value
        await self._async_send_value(command_value)


def _entities_for_device(
    device: CustomerDevice, manager: Manager, profile: DeviceProfile
) -> list[EigenNumber]:
    entities: list[EigenNumber] = []
    function = getattr(device, "function", {})
    status = getattr(device, "status", {})

    for definition in profile.entities:
        if definition.platform is not Platform.NUMBER:
            continue
        if definition.code not in function and definition.code not in status:
            continue
        entities.append(EigenNumber(device, manager, profile, definition))
    return entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Eigen number entities."""
    runtime: EigenRuntime = entry.runtime_data
    manager = runtime.manager
    if manager is None:
        return

    entities: list[EigenNumber] = []
    for device in manager.device_map.values():
        profile = get_profile(getattr(device, "product_id", None))
        if profile is None or profile.discovery_only:
            continue
        entities.extend(_entities_for_device(device, manager, profile))

    async_add_entities(entities)
