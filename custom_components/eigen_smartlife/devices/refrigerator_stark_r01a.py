"""Profile for Eigen Stark-R01A refrigerator."""

from homeassistant.components.number import NumberDeviceClass
from homeassistant.const import Platform, UnitOfTemperature


def _build_entities():
    from . import EntityProfile

    return (
        EntityProfile(
            platform=Platform.SWITCH,
            code="child_lock",
            translation_key="child_lock",
            icon="mdi:lock",
        ),
        EntityProfile(
            platform=Platform.SWITCH,
            code="switch_chiller",
            translation_key="chiller",
            icon="mdi:snowflake-thermometer",
        ),
        EntityProfile(
            platform=Platform.NUMBER,
            code="cool_temp_set",
            translation_key="fridge_temperature",
            icon="mdi:fridge-outline",
            minimum=2,
            maximum=8,
            step=1,
            unit=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
        ),
        EntityProfile(
            platform=Platform.NUMBER,
            code="cold_temp_set",
            translation_key="freezer_temperature",
            icon="mdi:snowflake",
            minimum=-50,
            maximum=20,
            step=1,
            unit=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
        ),
    )


REFRIGERATOR_ENTITIES = _build_entities()
