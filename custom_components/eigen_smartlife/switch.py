"""Switch entities for Eigen SmartLife."""

from __future__ import annotations

from tuya_sharing import CustomerDevice, Manager

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EigenRuntime
from .devices import DeviceProfile, get_profile
from .entity import EigenEntity


class EigenSwitch(EigenEntity, SwitchEntity):
    """Boolean Tuya DP exposed as a Home Assistant switch."""

    @property
    def is_on(self) -> bool | None:
        value = self._status()
        return value if isinstance(value, bool) else None

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_send_value(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_send_value(False)


def _entities_for_device(
    device: CustomerDevice, manager: Manager, profile: DeviceProfile
) -> list[EigenSwitch]:
    entities: list[EigenSwitch] = []
    function = getattr(device, "function", {})
    status = getattr(device, "status", {})

    for definition in profile.entities:
        if definition.platform is not Platform.SWITCH:
            continue
        if definition.code not in function and definition.code not in status:
            continue
        entities.append(EigenSwitch(device, manager, profile, definition))
    return entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Eigen switches."""
    runtime: EigenRuntime = entry.runtime_data
    manager = runtime.manager
    if manager is None:
        return

    entities: list[EigenSwitch] = []
    for device in manager.device_map.values():
        profile = get_profile(getattr(device, "product_id", None))
        if profile is None or profile.discovery_only:
            continue
        entities.extend(_entities_for_device(device, manager, profile))

    async_add_entities(entities)
