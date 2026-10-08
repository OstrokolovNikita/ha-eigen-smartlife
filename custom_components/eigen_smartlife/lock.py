"""Lock entities for Eigen SmartLife."""

from __future__ import annotations

from tuya_sharing import CustomerDevice, Manager

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EigenRuntime
from .devices import DeviceProfile, get_profile
from .entity import EigenEntity


class EigenLock(EigenEntity, LockEntity):
    """Boolean Tuya DP exposed as a Home Assistant lock."""

    @property
    def is_locked(self) -> bool | None:
        value = self._status()
        return value if isinstance(value, bool) else None

    async def async_lock(self, **kwargs) -> None:
        await self._async_send_value(True)

    async def async_unlock(self, **kwargs) -> None:
        await self._async_send_value(False)


def _entities_for_device(
    device: CustomerDevice, manager: Manager, profile: DeviceProfile
) -> list[EigenLock]:
    function = getattr(device, "function", {})
    status = getattr(device, "status", {})
    return [
        EigenLock(device, manager, profile, definition)
        for definition in profile.entities
        if definition.platform is Platform.LOCK
        and (definition.code in function or definition.code in status)
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Eigen lock entities."""
    runtime: EigenRuntime = entry.runtime_data
    manager = runtime.manager
    if manager is None:
        return

    entities: list[EigenLock] = []
    for device in manager.device_map.values():
        profile = get_profile(getattr(device, "product_id", None))
        if profile is None or profile.discovery_only:
            continue
        entities.extend(_entities_for_device(device, manager, profile))
    async_add_entities(entities)
