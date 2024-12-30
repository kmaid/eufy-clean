"""Data update coordinator for Eufy Clean."""
from datetime import timedelta
import logging
from typing import Any, Dict, Callable
import time
import json

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
        self._devices = []

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

    def _handle_mqtt_message(self, client: Any, userdata: Any, msg: Any) -> None:
        """Handle MQTT message."""
        try:
            _LOGGER.info("Received MQTT message - Topic: %s", msg.topic)

            # Parse the message
            try:
                payload = json.loads(msg.payload.decode())
                _LOGGER.debug("Parsed payload: %s", payload)
            except json.JSONDecodeError as err:
                _LOGGER.error("Failed to decode MQTT message: %s\nPayload: %s", err, msg.payload.decode())
                return

            # Extract device ID from topic (format: cmd/eufy_home/MODEL/ID/res)
            topic_parts = msg.topic.split("/")
            if len(topic_parts) >= 4:
                device_id = topic_parts[3]
                _LOGGER.info("Processing message for device: %s", device_id)
            else:
                _LOGGER.warning("Invalid topic format: %s", msg.topic)
                return

            # Extract data from payload
            if "payload" in payload:
                # Handle string or dict payload
                if isinstance(payload["payload"], str):
                    data = json.loads(payload["payload"])
                else:
                    data = payload["payload"]
                _LOGGER.info("Extracted data: %s", data)

                # Get DPS data
                if "data" in data:
                    dps = data["data"]
                    _LOGGER.info(
                        "DPS data for device %s:\n"
                        "Raw data: %s\n"
                        "DPS data: %s\n"
                        "Keys: %s",
                        device_id,
                        data,
                        dps,
                        list(dps.keys()) if isinstance(dps, dict) else "Not a dict"
                    )

                    # Check if we already know about this device
                    device = next((d for d in self._devices if d.get("device_sn") == device_id), None)
                    if not device:
                        # Get device info from cloud devices
                        cloud_device = next((d for d in self._devices if d.get("device_sn") == device_id), None)
                        if cloud_device:
                            _LOGGER.info("Found matching cloud device for MQTT device %s", device_id)
                            # Create new device entry from cloud data
                            device = {
                                "device_id": device_id,
                                "device_sn": device_id,
                                "name": cloud_device.get("deviceName", ""),
                                "model": cloud_device.get("deviceModel", ""),
                                "type": "mqtt",
                                "battery_level": 0,
                                "state": "unknown",
                                "is_online": True,
                                "raw_state": data,
                                "dps": dps,
                                "is_novel_api": False
                            }
                            self._devices.append(device)
                            _LOGGER.info("Added new device from MQTT: %s", device)
                        else:
                            _LOGGER.warning("Received MQTT update for unknown device: %s", device_id)
                            # Create basic device entry
                            device = {
                                "device_id": device_id,
                                "device_sn": device_id,
                                "name": data.get("deviceName", ""),
                                "model": data.get("deviceModel", ""),
                                "type": "mqtt",
                                "battery_level": 0,
                                "state": "unknown",
                                "is_online": True,
                                "raw_state": data,
                                "dps": dps,
                                "is_novel_api": False
                            }
                            self._devices.append(device)
                            _LOGGER.info("Added new device from MQTT without cloud data: %s", device)

                    # Update device data
                    if device:
                        _LOGGER.info("Updating device %s with new data", device_id)
                        device.update({
                            "raw_state": data,
                            "dps": dps,
                            "is_online": True,
                            "last_update": int(time.time() * 1000)
                        })

                        # Check for novel API
                        novel_dps_keys = ["152", "153", "154", "155", "158", "160", "163", "173", "177"]
                        if any(k in dps for k in novel_dps_keys):
                            _LOGGER.info("Novel API detected for device %s", device_id)
                            device["is_novel_api"] = True

                        # Schedule update on event loop
                        self.hass.loop.call_soon_threadsafe(
                            self.async_set_updated_data,
                            {"devices": self._devices}
                        )
                else:
                    _LOGGER.warning("No 'data' field in payload: %s", data)
            else:
                _LOGGER.warning("No 'payload' field in message: %s", payload)

        except Exception as err:
            _LOGGER.error("Error handling MQTT message: %s", err)

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            # First get cloud devices
            cloud_devices = await self.api.get_cloud_devices()
            _LOGGER.info("Got %d cloud devices from API", len(cloud_devices))

            # Update internal device list with cloud devices
            self._devices = cloud_devices

            # Then initialize MQTT connection if needed
            if not self.api.login.mqtt_connect and cloud_devices:
                _LOGGER.info("Initializing MQTT connection with %d cloud devices", len(cloud_devices))
                await self.api.init()
                # Set coordinator reference in MQTT connect
                if self.api.login.mqtt_connect:
                    self.api.login.mqtt_connect.coordinator = self
                    _LOGGER.info("Set coordinator reference in MQTT connect")
            elif not cloud_devices:
                _LOGGER.warning("No cloud devices found, skipping MQTT initialization")
            else:
                _LOGGER.debug("MQTT connection already initialized")

            # Get MQTT devices if connection is available
            if self.api.login.mqtt_connect:
                mqtt_devices = await self.api.get_mqtt_devices()
                _LOGGER.info("Got %d MQTT devices", len(mqtt_devices))

                # Update or add MQTT devices
                for mqtt_device in mqtt_devices:
                    device_id = mqtt_device.get("device_sn")
                    if not device_id:
                        continue

                    # Update existing device or add new one
                    existing_device = next((d for d in self._devices if d.get("device_sn") == device_id), None)
                    if existing_device:
                        existing_device.update(mqtt_device)
                        existing_device["type"] = "mqtt"
                    else:
                        mqtt_device["type"] = "mqtt"
                        self._devices.append(mqtt_device)

            _LOGGER.info("Total devices after update: %d", len(self._devices))
            return {"devices": self._devices}
        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise
