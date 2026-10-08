"""Runtime and push listeners for Eigen SmartLife."""

from __future__ import annotations

from typing import Any

import requests
from tuya_sharing import (
    CustomerDevice,
    Manager,
    SharingDeviceListener,
    SharingTokenListener,
)
from tuya_sharing.exceptions import ApiRequestException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.dispatcher import dispatcher_send

from .client import load_eigen_devices
from .const import (
    CONF_ENDPOINT,
    CONF_TERMINAL_ID,
    CONF_TOKEN_INFO,
    CONF_USER_CODE,
    LOGGER,
    SIGNAL_NEW_DEVICE,
    SIGNAL_REMOVE_DEVICE,
    SIGNAL_UPDATE,
    TUYA_CLIENT_ID,
)
from .devices import get_profile


class EigenTokenListener(SharingTokenListener):
    """Persist refreshed Tuya Device Sharing tokens in the config entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

    def update_token(self, token_info: dict[str, Any]) -> None:
        """Handle an SDK token refresh from its worker thread."""
        data = {
            **self.entry.data,
            CONF_TOKEN_INFO: {
                "t": token_info["t"],
                "uid": token_info["uid"],
                "expire_time": token_info["expire_time"],
                "access_token": token_info["access_token"],
                "refresh_token": token_info["refresh_token"],
            },
        }

        @callback
        def _update_entry() -> None:
            self.hass.config_entries.async_update_entry(self.entry, data=data)

        self.hass.add_job(_update_entry)


class EigenRuntime(SharingDeviceListener):
    """Own the Device Sharing manager and bridge push callbacks into HA."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.manager: Manager | None = None

    def initialize(self) -> None:
        """Initialize the blocking Tuya client in HA's executor."""
        token_listener = EigenTokenListener(self.hass, self.entry)
        manager = Manager(
            TUYA_CLIENT_ID,
            self.entry.data[CONF_USER_CODE],
            self.entry.data[CONF_TERMINAL_ID],
            self.entry.data[CONF_ENDPOINT],
            self.entry.data[CONF_TOKEN_INFO],
            token_listener,
        )
        manager.add_device_listener(self)

        try:
            load_eigen_devices(manager)
        except requests.exceptions.RequestException as err:
            raise ConfigEntryNotReady("Unable to connect to Tuya Device Sharing") from err
        except ApiRequestException as err:
            message = str(err).lower()
            if "sign invalid" in message:
                raise ConfigEntryAuthFailed(
                    "Tuya Device Sharing authentication expired"
                ) from err
            raise ConfigEntryNotReady(f"Tuya Device Sharing API error: {err}") from err

        self.manager = manager

    def update_device(
        self,
        device: CustomerDevice,
        updated_status_properties: list[str] | None = None,
        dp_timestamps: dict[str, int] | None = None,
    ) -> None:
        """Forward a Tuya cloud push update to entities."""
        if get_profile(getattr(device, "product_id", None)) is None:
            return
        dispatcher_send(
            self.hass,
            SIGNAL_UPDATE.format(device.id),
            updated_status_properties,
            dp_timestamps,
        )

    def add_device(self, device: CustomerDevice) -> None:
        """Forward newly shared supported Eigen devices."""
        if get_profile(getattr(device, "product_id", None)) is None:
            return
        dispatcher_send(self.hass, SIGNAL_NEW_DEVICE, device)

    def remove_device(self, device_id: str) -> None:
        """Forward removal of a shared device."""
        dispatcher_send(self.hass, SIGNAL_REMOVE_DEVICE.format(device_id))

    def start_push(self) -> None:
        """Start Tuya cloud push after entities mark their devices as in use."""
        if self.manager is None:
            return
        self.manager.refresh_mq()

    def shutdown(self) -> None:
        """Stop push and detach listeners without revoking the account grant."""
        if self.manager is None:
            return
        if self.manager.mq is not None:
            self.manager.mq.stop()
        self.manager.remove_device_listener(self)
