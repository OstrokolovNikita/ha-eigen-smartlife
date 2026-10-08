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


def _enrich_device(manager: Manager, device: CustomerDevice) -> None:
    """Fetch Device Sharing specification/strategy data for diagnostics."""
    product_id = getattr(device, "product_id", None)

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


def load_eigen_devices(manager: Manager) -> list[CustomerDevice]:
    """Load supported entities while discovering all Smart Life devices.

    Only devices with an explicit Eigen SmartLife profile are inserted into the
    manager cache and exposed in Home Assistant. All authorized Smart Life
    devices are enriched into a separate diagnostics snapshot so new profiles
    can be built from real DP data without guessing.
    """
    manager.device_map.clear()
    homes = manager.home_repository.query_homes()
    manager.user_homes = homes

    discovered_devices: list[CustomerDevice] = []

    for home in homes:
        response = manager.customer_api.get(
            "/v1.0/m/life/ha/home/devices", {"homeId": home.id}
        )
        if not response or not response.get("success"):
            continue

        for raw_device in response.get("result", []):
            device = CustomerDevice(**raw_device)
            _normalize_status(device)
            _enrich_device(manager, device)
            discovered_devices.append(device)

            if getattr(device, "product_id", None) in PROFILES:
                manager.device_map[device.id] = device

    return discovered_devices
