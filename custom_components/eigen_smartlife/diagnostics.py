"""Diagnostics for Eigen SmartLife."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from tuya_sharing import CustomerDevice

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import EigenRuntime
from .devices import get_profile


def _safe_device_id(device_id: str) -> str:
    return sha256(device_id.encode()).hexdigest()[:12]


def _namespace_map(value: Any) -> Any:
    """Convert SDK SimpleNamespace maps to JSON-safe diagnostic data."""
    if isinstance(value, dict):
        return {str(key): _namespace_map(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_namespace_map(item) for item in value]
    if hasattr(value, "__dict__"):
        return {
            str(key): _namespace_map(item)
            for key, item in vars(value).items()
            if key not in {"local_key", "uuid", "ip", "asset_id"}
        }
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _device_data(device: CustomerDevice) -> dict[str, Any]:
    """Return useful DP diagnostics without credentials or local secrets."""
    return {
        "id_hash": _safe_device_id(device.id),
        "name": device.name,
        "category": getattr(device, "category", None),
        "product_id": getattr(device, "product_id", None),
        "product_name": getattr(device, "product_name", None),
        "online": getattr(device, "online", None),
        "support_local": getattr(device, "support_local", False),
        "status": _namespace_map(getattr(device, "status", {})),
        "function": _namespace_map(getattr(device, "function", {})),
        "status_range": _namespace_map(getattr(device, "status_range", {})),
        "local_strategy": _namespace_map(getattr(device, "local_strategy", {})),
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return sanitized integration diagnostics."""
    runtime: EigenRuntime = entry.runtime_data
    manager = runtime.manager
    if manager is None:
        return {"connected": False, "devices": []}

    mqtt_connected = False
    if manager.mq is not None and manager.mq.client is not None:
        mqtt_connected = bool(manager.mq.client.is_connected())

    return {
        "connected": True,
        "endpoint": manager.customer_api.endpoint,
        "mqtt_connected": mqtt_connected,
        "devices": [
            _device_data(device)
            for device in manager.device_map.values()
            if get_profile(getattr(device, "product_id", None)) is not None
        ],
    }
