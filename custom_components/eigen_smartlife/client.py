"""Tuya Device Sharing client helpers for Eigen SmartLife."""

from __future__ import annotations

from typing import Any

from tuya_sharing import CustomerDevice, Manager
from tuya_sharing.exceptions import ApiRequestException

from .const import LOGGER
from .devices import PROFILES


def _normalize_status(device: CustomerDevice) -> None:
    """Normalize the SDK's list-form status into a code -> value mapping."""
    if isinstance(device.status, dict):
        return

    normalized: dict[str, Any] = {}
    if isinstance(device.status, list):
        for item in device.status:
            if isinstance(item, dict) and "code" in item and "value" in item:
                normalized[str(item["code"])] = item["value"]
    device.status = normalized


def load_eigen_devices(manager: Manager) -> None:
    """Load only known Eigen products into the manager cache.

    This intentionally avoids Manager.update_device_cache(), which enriches every
    Tuya device in the user's homes. Eigen SmartLife is product-scoped and should
    neither enumerate nor process unrelated Smart Life devices.
    """
    manager.device_map.clear()
    homes = manager.home_repository.query_homes()
    manager.user_homes = homes

    for home in homes:
        response = manager.customer_api.get(
            "/v1.0/m/life/ha/home/devices", {"homeId": home.id}
        )
        if not response or not response.get("success"):
            continue

        for raw_device in response.get("result", []):
            product_id = raw_device.get("product_id")
            if product_id not in PROFILES:
                continue

            device = CustomerDevice(**raw_device)
            _normalize_status(device)

            # Enrichment APIs vary by product. One unsupported endpoint must not
            # prevent the whole integration from starting.
            for updater_name in (
                "update_device_specification",
                "update_device_strategy_info",
                "update_device_report_type",
            ):
                updater = getattr(manager.device_repository, updater_name)
                try:
                    updater(device)
                except ApiRequestException as err:
                    LOGGER.debug(
                        "Tuya enrichment %s unavailable for %s (%s): %s",
                        updater_name,
                        product_id,
                        device.id,
                        err,
                    )
                except (KeyError, TypeError, ValueError) as err:
                    LOGGER.debug(
                        "Unexpected Tuya enrichment payload in %s for %s (%s): %s",
                        updater_name,
                        product_id,
                        device.id,
                        err,
                    )

            manager.device_map[device.id] = device
