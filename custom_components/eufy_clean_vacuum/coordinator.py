"""Data update coordinator for Eufy Clean."""
from datetime import timedelta
import logging
from typing import Any, Dict, Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EufyCleanApi

_LOGGER = logging.getLogger(__name__)

class EufyCleanDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api: EufyCleanApi) -> None:
        """Initialize."""
        self.api = api
        self.platforms: list[str] = []
        self._device_listeners: Dict[str, Callable] = {}
        self._data = {"devices": {}}

        super().__init__(
            hass,
            _LOGGER,
            name="Eufy Clean",
            update_interval=timedelta(minutes=5),  # Slower rate for cloud updates
        )

        # Set up MQTT message callback
        if hasattr(self.api.login, 'mqtt_connect') and self.api.login.mqtt_connect:
            _LOGGER.info("MQTT connection available, setting up real-time updates")
            self.api.login.mqtt_connect.client.on_message = self._handle_mqtt_message
        else:
            _LOGGER.warning("No MQTT connection available, devices will update via cloud only")

    @callback
    def _handle_mqtt_message(self, client: Any, userdata: Any, msg: Any) -> None:
        """Handle incoming MQTT message."""
        try:
            import json
            payload = json.loads(msg.payload.decode())
            _LOGGER.info("Received MQTT message - Topic: %s, Full Payload: %s", msg.topic, payload)

            if "payload" in payload and "data" in payload["payload"]:
                data = payload["payload"]["data"]
                device_id = msg.topic.split("/")[3]  # Extract device ID from topic
                _LOGGER.info("Processing MQTT update - Device ID: %s, Data: %s", device_id, data)

                # Update device data
                if device_id in self._data["devices"]:
                    device_data = self._data["devices"][device_id]
                    old_state = device_data.get("state")
                    old_battery = device_data.get("battery_level")

                    # Extract DPS data
                    dps = data.get("dps", {})
                    _LOGGER.info(
                        "MQTT DPS data for device %s:\n"
                        "- Raw DPS: %s\n"
                        "- Legacy Work Status (15): %s\n"
                        "- Novel Work Status (153): %s\n"
                        "- Legacy Battery (104): %s\n"
                        "- Novel Battery (163): %s",
                        device_id,
                        dps,
                        dps.get("15"),
                        dps.get("153"),
                        dps.get("104"),
                        dps.get("163")
                    )

                    # Get state from DPS data
                    work_status = dps.get("15") or dps.get("153")  # Try both legacy and novel DPS IDs
                    battery_level = dps.get("104") or dps.get("163")  # Try both legacy and novel DPS IDs

                    device_data.update({
                        "battery_level": battery_level or device_data.get("battery_level", 0),
                        "state": work_status or device_data.get("state", "unknown"),
                        "is_online": True,
                        "raw_state": data,
                        "dps": dps
                    })

                    _LOGGER.info(
                        "Device %s (%s) state update:\n"
                        "- State: %s -> %s\n"
                        "- Battery: %s -> %s\n"
                        "- DPS: %s\n"
                        "- Raw State: %s",
                        device_data.get("name", device_id),
                        device_id,
                        old_state,
                        device_data["state"],
                        old_battery,
                        device_data["battery_level"],
                        dps,
                        data
                    )

                    # Notify listeners
                    self.async_set_updated_data(self._data)
                else:
                    _LOGGER.warning("Received MQTT update for unknown device: %s", device_id)
            else:
                _LOGGER.warning("Unexpected MQTT message format - Payload: %s", payload)
        except Exception as err:
            _LOGGER.error("Error handling MQTT message: %s\nPayload: %s", err, msg.payload.decode())

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            _LOGGER.debug("Starting periodic update of devices")

            # Get both cloud and MQTT devices
            cloud_devices = await self.api.get_cloud_devices()
            mqtt_devices = await self.api.get_mqtt_devices()

            _LOGGER.info("Found %d cloud devices and %d MQTT devices", len(cloud_devices), len(mqtt_devices))

            devices = self._data["devices"].copy()  # Preserve existing MQTT data

            # Process cloud devices
            for device in cloud_devices:
                device_sn = device.get("device_sn")
                if device_sn:
                    dps = device.get("dps", {})
                    _LOGGER.info(
                        "Processing cloud device - SN: %s, Name: %s, Model: %s, DPS: %s",
                        device_sn,
                        device.get("deviceName", "Unknown"),
                        device.get("deviceModel", "Unknown"),
                        dps
                    )

                    # Get state from DPS data
                    work_status = dps.get("15") or dps.get("153")  # Try both legacy and novel DPS IDs
                    battery_level = dps.get("104") or dps.get("163")  # Try both legacy and novel DPS IDs

                    devices[device_sn] = {
                        "device_id": device_sn,  # Keep device_id for backward compatibility
                        "device_sn": device_sn,
                        "name": device.get("deviceName", ""),
                        "model": device.get("deviceModel", ""),
                        "type": "cloud",
                        "battery_level": battery_level or 0,
                        "state": work_status or "unknown",
                        "is_online": device.get("online", False),
                        "raw_state": device.get("raw_data", {}),
                        "dps": dps
                    }
                else:
                    _LOGGER.warning("Found cloud device without SN: %s", device)

            # Process MQTT devices (only update if not recently updated by MQTT)
            for device in mqtt_devices:
                device_sn = device.get("device_sn")
                if device_sn and device_sn not in devices:
                    dps = device.get("dps", {})
                    _LOGGER.info(
                        "Processing MQTT device - SN: %s, Name: %s, Model: %s, DPS: %s",
                        device_sn,
                        device.get("deviceName", "Unknown"),
                        device.get("deviceModel", "Unknown"),
                        dps
                    )

                    # Get state from DPS data
                    work_status = dps.get("15") or dps.get("153")  # Try both legacy and novel DPS IDs
                    battery_level = dps.get("104") or dps.get("163")  # Try both legacy and novel DPS IDs

                    devices[device_sn] = {
                        "device_id": device_sn,  # Keep device_id for backward compatibility
                        "device_sn": device_sn,
                        "name": device.get("deviceName", ""),
                        "model": device.get("deviceModel", ""),
                        "type": "mqtt",
                        "battery_level": battery_level or 0,
                        "state": work_status or "unknown",
                        "is_online": True,  # MQTT devices are always online when we receive data
                        "raw_state": device,
                        "dps": dps
                    }
                else:
                    if not device_sn:
                        _LOGGER.warning("Found MQTT device without SN: %s", device)
                    else:
                        _LOGGER.debug("Skipping MQTT device %s as it was recently updated", device_sn)

            _LOGGER.info("Total devices after update: %d", len(devices))
            for device_sn, device in devices.items():
                _LOGGER.info(
                    "Device status - SN: %s, Name: %s, Type: %s, Online: %s, State: %s, DPS: %s",
                    device_sn,
                    device.get("name", "Unknown"),
                    device.get("type", "unknown"),
                    device.get("is_online", False),
                    device.get("state", "unknown"),
                    device.get("dps", {})
                )

            self._data = {"devices": devices}
            return self._data
        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
