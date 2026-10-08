"""Profile for Smart Life Measure socket (PID 999hv2s5ckom5zw2)."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import (
    Platform,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityCategory


def _build_entities():
    from . import EntityProfile

    return (
        EntityProfile(
            platform=Platform.SWITCH,
            code="switch_1",
            translation_key="outlet",
            icon="mdi:power-socket-eu",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        EntityProfile(
            platform=Platform.SENSOR,
            code="cur_power",
            translation_key="power",
            icon="mdi:flash",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        EntityProfile(
            platform=Platform.SENSOR,
            code="cur_voltage",
            translation_key="voltage",
            icon="mdi:sine-wave",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        EntityProfile(
            platform=Platform.SENSOR,
            code="cur_current",
            translation_key="current",
            icon="mdi:current-ac",
            unit=UnitOfElectricCurrent.MILLIAMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        EntityProfile(
            platform=Platform.SENSOR,
            code="add_ele",
            translation_key="energy",
            icon="mdi:lightning-bolt-circle",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        EntityProfile(
            platform=Platform.BINARY_SENSOR,
            code="fault",
            translation_key="problem",
            icon="mdi:alert-circle-outline",
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        EntityProfile(
            platform=Platform.LOCK,
            code="child_lock",
            translation_key="child_lock",
            icon="mdi:hand-back-left",
            entity_category=EntityCategory.CONFIG,
        ),
        EntityProfile(
            platform=Platform.SELECT,
            code="relay_status",
            translation_key="restore_state",
            icon="mdi:power-settings",
            entity_category=EntityCategory.CONFIG,
            options=("power_off", "power_on", "last"),
        ),
        EntityProfile(
            platform=Platform.SELECT,
            code="light_mode",
            translation_key="indicator_mode",
            icon="mdi:led-on",
            entity_category=EntityCategory.CONFIG,
            options=("relay", "pos", "none"),
        ),
        EntityProfile(
            platform=Platform.NUMBER,
            code="countdown_1",
            translation_key="countdown",
            icon="mdi:timer-outline",
            minimum=0,
            maximum=86400,
            step=1,
            unit=UnitOfTime.SECONDS,
            device_class=NumberDeviceClass.DURATION,
            entity_category=EntityCategory.CONFIG,
        ),
    )


MEASURE_SOCKET_ENTITIES = _build_entities()
