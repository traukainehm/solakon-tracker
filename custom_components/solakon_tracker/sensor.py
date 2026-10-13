from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfEnergy, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SolakonCoordinator
from .const import CONF_HOST, DOMAIN


@dataclass(frozen=True, kw_only=True)
class SolakonSensorDescription(SensorEntityDescription):
    section: str
    value_key: str


SENSORS = (
    SolakonSensorDescription(
        key="instantaneous_power_w",
        name="Instantaneous power",
        section="extracted",
        value_key="instantaneous_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolakonSensorDescription(
        key="instantaneous_power_l1_w",
        name="Phase 1 power",
        section="extracted",
        value_key="instantaneous_power_l1_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolakonSensorDescription(
        key="instantaneous_power_l2_w",
        name="Phase 2 power",
        section="extracted",
        value_key="instantaneous_power_l2_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolakonSensorDescription(
        key="instantaneous_power_l3_w",
        name="Phase 3 power",
        section="extracted",
        value_key="instantaneous_power_l3_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolakonSensorDescription(
        key="energy_summation_kwh",
        name="Energy total",
        section="extracted",
        value_key="energy_summation_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SolakonSensorDescription(
        key="negative_energy_summation_kwh",
        name="Energy returned to grid",
        section="extracted",
        value_key="negative_energy_summation_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SolakonSensorDescription(
        key="meter",
        name="Meter",
        section="extracted",
        value_key="meter",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SolakonSensorDescription(
        key="hardware",
        name="Hardware",
        section="device",
        value_key="hw",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SolakonSensorDescription(
        key="hardware_revision",
        name="Hardware revision",
        section="device",
        value_key="hw_rev",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SolakonSensorDescription(
        key="firmware",
        name="Firmware version",
        section="device",
        value_key="fw_ver",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SolakonSensorDescription(
        key="serial_number",
        name="Serial number",
        section="device",
        value_key="hw_sn",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SolakonSensorDescription(
        key="wifi_mac",
        name="Wi-Fi MAC address",
        section="device",
        value_key="wifi_mac",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SolakonSensorDescription(
        key="uptime",
        name="Uptime",
        section="device",
        value_key="uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SolakonCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SolakonSensor(coordinator, entry.data[CONF_HOST], description)
        for description in SENSORS
    )


class SolakonSensor(CoordinatorEntity[SolakonCoordinator], SensorEntity):
    entity_description: SolakonSensorDescription

    def __init__(
        self,
        coordinator: SolakonCoordinator,
        host: str,
        description: SolakonSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{host}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name="Solakon Tracker",
            manufacturer="Solakon",
            model=coordinator.data.get("device", {}).get("hw"),
            sw_version=coordinator.data.get("device", {}).get("fw_ver"),
            serial_number=coordinator.data.get("device", {}).get("hw_sn"),
            configuration_url=host,
        )

    @property
    def native_value(self) -> Any:
        section = self.coordinator.data.get(self.entity_description.section, {})
        if not isinstance(section, dict):
            return None
        return section.get(self.entity_description.value_key)