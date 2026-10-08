"""Binary sensor entities for Eigen SmartLife."""

from __future__ import annotations

from tuya_sharing import CustomerDevice, Manager

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EigenRuntime
from .devices import DeviceProfile, EntityProfile, get_profile
from .entity import EigenEntity


class EigenBinarySensor(EigenEntity, BinarySensorEntity):
    """Tuya bitmap/boolean exposed as a binary sensor."""

    def __init__(
        self,
        device: CustomerDevice,
        manager: Manager,
        device_profile: DeviceProfile,
        entity_profile: EntityProfile,
    ) -> None:
        super().__init__(device, manager, device_profile, entity_profile)
        self._attr_device_class = entity_profile.device_class

    @property
    def is_on(self) -> bool | None:
        value = self._status()
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        return None

    @property
    def extra_state_attributes(self) -> dict[str, int] | None:
        value = self._status()
        if isinstance(value, int):
            return {"fault_code": value}
        return None


def _entities_for_device(
    device: CustomerDevice, manager: Manager, profile: DeviceProfile
) -> list[EigenBinarySensor]:
    status = getattr(device, "status", {})
    return [
        EigenBinarySensor(device, manager, profile, definition)
        for definition in profile.entities
        if definition.platform is Platform.BINARY_SENSOR
        and definition.code in status
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Eigen binary sensors."""
    runtime: EigenRuntime = entry.runtime_data
    manager = runtime.manager
    if manager is None:
        return

    entities: list[EigenBinarySensor] = []
    for device in manager.device_map.values():
        profile = get_profile(getattr(device, "product_id", None))
        if profile is None or profile.discovery_only:
            continue
        entities.extend(_entities_for_device(device, manager, profile))
    async_add_entities(entities)
