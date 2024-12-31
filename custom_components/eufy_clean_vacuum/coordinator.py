"""Data update coordinator for Eufy Clean."""
from datetime import timedelta
import logging
from typing import Any, Dict, Callable
import time
import json
import base64
from google.protobuf import json_format
from google.protobuf.message import Message
from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.json_format import MessageToDict

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
        self.hass = hass  # Store hass reference for thread-safe updates
        self._proto_pool = None
        self._init_proto_pool()

        super().__init__(
            hass,
            _LOGGER,
            name="Eufy Clean",
            update_interval=timedelta(minutes=5),  # Slower rate for cloud updates
        )

    def _init_proto_pool(self) -> None:
        """Initialize the protobuf descriptor pool."""
        try:
            self._proto_pool = DescriptorPool()
            # Load work_status.proto
            with open("custom_components/eufy_clean_vacuum/proto/cloud/work_status.proto", "r") as f:
                self._proto_pool.Add(f.read())
        except Exception as err:
            _LOGGER.error("Failed to initialize protobuf pool: %s", err)

    def _decode_proto_message(self, proto_data: str, message_type: str) -> Dict[str, Any]:
        """Decode a protobuf message."""
        try:
            if not self._proto_pool:
                _LOGGER.error("Protobuf pool not initialized")
                return {}

            # Decode base64 to bytes
            proto_bytes = base64.b64decode(proto_data)

            # Get the message descriptor and create a new message
            message_descriptor = self._proto_pool.FindMessageTypeByName(f"proto.cloud.{message_type}")
            message = Message()
            message.ParseFromString(proto_bytes)

            # Convert to dictionary
            return MessageToDict(message)
        except Exception as err:
            _LOGGER.error("Failed to decode protobuf message: %s", err)
            return {}

    async def async_setup(self) -> None:
        """Set up the coordinator."""
        try:
            # First initialize the API
            _LOGGER.info("Initializing API")
            await self.api.init()

            # Get cloud devices first
            cloud_devices = await self.api.get_cloud_devices()
            _LOGGER.info("Raw cloud devices response: %s", cloud_devices)

            if isinstance(cloud_devices, dict):
                _LOGGER.info("Cloud devices response is a dict with keys: %s", list(cloud_devices.keys()))
                if "devices" in cloud_devices:
                    cloud_devices = cloud_devices["devices"]
                    _LOGGER.info("Extracted devices from response: %s", cloud_devices)

            _LOGGER.info("Got %d cloud devices from API", len(cloud_devices) if cloud_devices else 0)

            # Update internal device list with cloud devices
            self._devices = []
            if cloud_devices:
                for device in cloud_devices:
                    _LOGGER.info("Processing cloud device: %s", device)
                    device["type"] = "cloud"
                    self._devices.append(device)

            # Initialize MQTT connection if we have cloud devices
            if cloud_devices:
                _LOGGER.info("Found cloud devices, initializing MQTT connection")
                if not self.api.login.mqtt_connect:
                    await self.api.init()

                # Set up MQTT message callback if available
                if hasattr(self.api.login, 'mqtt_connect') and self.api.login.mqtt_connect:
                    _LOGGER.info("MQTT connection available, setting up real-time updates")
                    self.api.login.mqtt_connect.coordinator = self
                    self.api.login.mqtt_connect.client.on_message = self._handle_mqtt_message
                else:
                    _LOGGER.warning("No MQTT connection available, devices will update via cloud only")

                # Get MQTT devices if connection is available
                if hasattr(self.api.login, 'mqtt_connect') and self.api.login.mqtt_connect:
                    mqtt_devices = self.api.login.mqtt_devices  # Use devices from login class
                    _LOGGER.info("Got %d MQTT devices", len(mqtt_devices))

                    # Update or add MQTT devices
                    for mqtt_device in mqtt_devices:
                        device_id = mqtt_device.get("device_sn")
                        if not device_id:
                            continue

                        # Update existing device or add new one
                        existing_device = next((d for d in self._devices if d.get("device_sn") == device_id), None)
                        if existing_device:
                            mqtt_device["type"] = "mqtt"
                            existing_device.update(mqtt_device)
                        else:
                            mqtt_device["type"] = "mqtt"
                            self._devices.append(mqtt_device)

            _LOGGER.info("Total devices after setup: %d", len(self._devices))
            for device in self._devices:
                _LOGGER.info(
                    "Device: %s (Type: %s, Model: %s, Name: %s, Raw: %s)",
                    device.get("device_sn"),
                    device.get("type"),
                    device.get("deviceModel"),
                    device.get("deviceName", "Unknown"),
                    device
                )

            # Set initial data
            self.async_set_updated_data({"devices": self._devices})

        except Exception as err:
            _LOGGER.error("Error setting up coordinator: %s", err)
            raise

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
                device_model = topic_parts[2] if len(topic_parts) >= 3 else ""
                _LOGGER.info("Processing message for device: %s (Model: %s)", device_id, device_model)
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

                    # Find existing device or create new one
                    device = next((d for d in self._devices if d.get("device_sn") == device_id), None)
                    if not device:
                        # Get device info from cloud devices
                        cloud_device = next((d for d in self._devices if d.get("device_sn") == device_id), None)
                        if cloud_device:
                            device = dict(cloud_device)  # Create a copy of cloud device data
                            device.update({
                                "type": "mqtt",
                                "mqtt": True,
                                "is_online": True
                            })
                            _LOGGER.info("Created MQTT device from cloud data: %s", device)
                        else:
                            device = {
                                "device_sn": device_id,
                                "deviceModel": device_model,
                                "deviceName": "",
                                "type": "mqtt",
                                "mqtt": True,
                                "is_online": True,
                                "state": "unknown",
                                "battery_level": None,
                                "is_novel_api": True
                            }
                            self._devices.append(device)
                            _LOGGER.info("Created new MQTT device: %s", device)

                    # Preserve existing DPS data and update with new values
                    current_dps = device.get("dps", {})
                    if isinstance(current_dps, dict) and isinstance(dps, dict):
                        current_dps.update(dps)
                    else:
                        current_dps = dps

                    # Update device data
                    device.update({
                        "raw_state": data,
                        "dps": current_dps,
                        "is_online": True,
                        "last_update": int(time.time() * 1000),
                        "mqtt": True
                    })

                    # Extract battery level
                    if "163" in current_dps:  # Novel API battery
                        device["battery_level"] = current_dps["163"]
                    elif "104" in current_dps:  # Legacy API battery
                        device["battery_level"] = current_dps["104"]

                    # Extract state from protobuf for Novel API
                    state = "unknown"
                    if "153" in current_dps:  # Novel API state
                        work_status = current_dps["153"]
                        if isinstance(work_status, str):  # It's a base64 encoded protobuf
                            decoded_status = self._decode_proto_message(work_status, "WorkStatus")
                            _LOGGER.debug("Decoded work status: %s", decoded_status)

                            if decoded_status:
                                # Map protobuf state to vacuum state
                                state_map = {
                                    "STANDBY": "standby",
                                    "SLEEP": "sleep",
                                    "FAULT": "error",
                                    "CHARGING": "charging",
                                    "FAST_MAPPING": "cleaning",  # Mapping is considered cleaning
                                    "CLEANING": "cleaning",
                                    "REMOTE_CTRL": "cleaning",  # Remote control is considered cleaning
                                    "GO_HOME": "returning",
                                    "CRUISIING": "cleaning"  # Cruising is considered cleaning
                                }
                                proto_state = decoded_status.get("state")
                                if proto_state:
                                    state = state_map.get(proto_state, "unknown")
                                    _LOGGER.debug("Mapped state %s to %s", proto_state, state)

                                # Store the full decoded status for advanced features
                                device["work_status"] = decoded_status
                        elif isinstance(work_status, (int, str)):
                            if str(work_status) == "1":
                                state = "cleaning"
                            elif str(work_status) == "2":
                                state = "charging"
                            elif str(work_status) == "3":
                                state = "paused"
                            elif str(work_status) == "4":
                                state = "standby"
                        _LOGGER.debug("Novel API work status: %s -> %s", work_status, state)
                    elif "15" in current_dps:  # Legacy API state
                        state = str(current_dps["15"]).lower()
                        _LOGGER.debug("Legacy API state: %s", state)

                    device["state"] = state

                    # Check for novel API
                    novel_dps_keys = ["152", "153", "154", "155", "158", "160", "163", "173", "177", "179"]
                    if any(k in current_dps for k in novel_dps_keys):
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
            # Get cloud devices first
            cloud_devices = await self.api.get_cloud_devices()
            _LOGGER.info("Raw cloud devices response: %s", cloud_devices)

            if isinstance(cloud_devices, dict):
                _LOGGER.info("Cloud devices response is a dict with keys: %s", list(cloud_devices.keys()))
                if "devices" in cloud_devices:
                    cloud_devices = cloud_devices["devices"]
                    _LOGGER.info("Extracted devices from response: %s", cloud_devices)

            _LOGGER.info("Got %d cloud devices from API", len(cloud_devices) if cloud_devices else 0)

            # Update internal device list with cloud devices
            self._devices = []
            if cloud_devices:
                for device in cloud_devices:
                    _LOGGER.info("Processing cloud device: %s", device)
                    device["type"] = "cloud"
                    self._devices.append(device)

            # Get MQTT devices if connection is available
            if hasattr(self.api.login, 'mqtt_connect') and self.api.login.mqtt_connect:
                mqtt_devices = self.api.login.mqtt_devices  # Use devices from login class
                _LOGGER.info("Got %d MQTT devices", len(mqtt_devices))

                # Update or add MQTT devices
                for mqtt_device in mqtt_devices:
                    device_id = mqtt_device.get("device_sn")
                    if not device_id:
                        continue

                    # Update existing device or add new one
                    existing_device = next((d for d in self._devices if d.get("device_sn") == device_id), None)
                    if existing_device:
                        mqtt_device["type"] = "mqtt"
                        existing_device.update(mqtt_device)
                    else:
                        mqtt_device["type"] = "mqtt"
                        self._devices.append(mqtt_device)

            _LOGGER.info("Total devices after update: %d", len(self._devices))
            for device in self._devices:
                _LOGGER.info(
                    "Device: %s (Type: %s, Model: %s, Name: %s, Raw: %s)",
                    device.get("device_sn"),
                    device.get("type"),
                    device.get("deviceModel"),
                    device.get("deviceName", "Unknown"),
                    device
                )
            return {"devices": self._devices}

        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise
