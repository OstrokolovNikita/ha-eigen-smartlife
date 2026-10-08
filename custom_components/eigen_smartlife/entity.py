"""Base entities for Eigen SmartLife."""

from __future__ import annotations

from typing import Any

from tuya_sharing import CustomerDevice, Manager

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SIGNAL_UPDATE
from .devices import DeviceProfile, EntityProfile


class EigenEntity(Entity):
    """Base class for one Eigen SmartLife DP entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        device: CustomerDevice,
        manager: Manager,
        device_profile: DeviceProfile,
        entity_profile: EntityProfile,
    ) -> None:
        self.device = device
        self.manager = manager
        self.device_profile = device_profile
        self.entity_profile = entity_profile

        self._attr_unique_id = f"{device.id}_{entity_profile.code}"
        self._attr_translation_key = entity_profile.translation_key
        self._attr_icon = entity_profile.icon
        self._attr_entity_category = entity_profile.entity_category
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            manufacturer=device_profile.manufacturer,
            name=device.name,
            model=device_profile.model,
        )

        # Manager.refresh_mq() subscribes only devices used by an entity.
        device.set_up = True

    @property
    def available(self) -> bool:
        """Return cloud online state."""
        return bool(getattr(self.device, "online", False))

    async def async_added_to_hass(self) -> None:
        """Subscribe to push state updates."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_UPDATE.format(self.device.id),
                self._handle_update,
            )
        )

    async def _handle_update(
        self,
        updated_status_properties: list[str] | None,
        dp_timestamps: dict[str, int] | None,
    ) -> None:
        """Write state when this DP or availability changed."""
        if (
            updated_status_properties is None
            or self.entity_profile.code in updated_status_properties
        ):
            self.async_write_ha_state()

    def _status(self) -> Any:
        """Return the current DP status value."""
        status = getattr(self.device, "status", {})
        if not isinstance(status, dict):
            return None
        return status.get(self.entity_profile.code)

    async def _async_send_value(self, value: Any) -> None:
        """Send a DP command using the Device Sharing API."""
        await self.hass.async_add_executor_job(
            self.manager.send_commands,
            self.device.id,
            [{"code": self.entity_profile.code, "value": value}],
        )
