"""Select entities for Eigen SmartLife."""

from __future__ import annotations

import json

from tuya_sharing import CustomerDevice, Manager

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EigenRuntime
from .devices import DeviceProfile, EntityProfile, get_profile
from .entity import EigenEntity


def _live_options(device: CustomerDevice, profile: EntityProfile) -> list[str]:
    function = getattr(device, "function", {})
    specification = function.get(profile.code) if isinstance(function, dict) else None
    values = getattr(specification, "values", None)
    if values:
        try:
            parsed = json.loads(values) if isinstance(values, str) else values
        except (TypeError, json.JSONDecodeError):
            parsed = None
        if isinstance(parsed, dict) and isinstance(parsed.get("range"), list):
            return [str(option) for option in parsed["range"]]
    return list(profile.options)


class EigenSelect(EigenEntity, SelectEntity):
    """Enum Tuya DP exposed as a Home Assistant select."""

    def __init__(
        self,
        device: CustomerDevice,
        manager: Manager,
        device_profile: DeviceProfile,
        entity_profile: EntityProfile,
    ) -> None:
        super().__init__(device, manager, device_profile, entity_profile)
        self._attr_options = _live_options(device, entity_profile)

    @property
    def current_option(self) -> str | None:
        value = self._status()
        return value if isinstance(value, str) else None

    async def async_select_option(self, option: str) -> None:
        await self._async_send_value(option)


def _entities_for_device(
    device: CustomerDevice, manager: Manager, profile: DeviceProfile
) -> list[EigenSelect]:
    function = getattr(device, "function", {})
    status = getattr(device, "status", {})
    return [
        EigenSelect(device, manager, profile, definition)
        for definition in profile.entities
        if definition.platform is Platform.SELECT
        and (definition.code in function or definition.code in status)
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Eigen select entities."""
    runtime: EigenRuntime = entry.runtime_data
    manager = runtime.manager
    if manager is None:
        return

    entities: list[EigenSelect] = []
    for device in manager.device_map.values():
        profile = get_profile(getattr(device, "product_id", None))
        if profile is None or profile.discovery_only:
            continue
        entities.extend(_entities_for_device(device, manager, profile))
    async_add_entities(entities)
