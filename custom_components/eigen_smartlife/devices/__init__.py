"""Device profiles for Eigen SmartLife."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.const import Platform

from ..const import (
    PRODUCT_ID_DISHWASHER_BD_ED,
    PRODUCT_ID_REFRIGERATOR_STARK_R01A,
)


@dataclass(frozen=True, slots=True)
class EntityProfile:
    """Describe one Home Assistant entity backed by a Tuya DP code."""

    platform: Platform
    code: str
    translation_key: str
    icon: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    step: float | None = None
    unit: str | None = None


@dataclass(frozen=True, slots=True)
class DeviceProfile:
    """Describe a supported Eigen product."""

    product_id: str
    model: str
    entities: tuple[EntityProfile, ...]
    discovery_only: bool = False


# Import concrete profiles only after the shared dataclasses exist.
from .refrigerator_stark_r01a import REFRIGERATOR_ENTITIES  # noqa: E402


PROFILES: dict[str, DeviceProfile] = {
    PRODUCT_ID_REFRIGERATOR_STARK_R01A: DeviceProfile(
        product_id=PRODUCT_ID_REFRIGERATOR_STARK_R01A,
        model="Eigen Stark-R01A",
        entities=REFRIGERATOR_ENTITIES,
    ),
    # Kept discovery-only until real Device Sharing API DP data is captured.
    # We intentionally do not guess entities from the Smart Life UI.
    PRODUCT_ID_DISHWASHER_BD_ED: DeviceProfile(
        product_id=PRODUCT_ID_DISHWASHER_BD_ED,
        model="Eigen BD/ED / Foss",
        entities=(),
        discovery_only=True,
    ),
}


def get_profile(product_id: str | None) -> DeviceProfile | None:
    """Return the Eigen profile for a Tuya product ID."""
    if not product_id:
        return None
    return PROFILES.get(product_id)
