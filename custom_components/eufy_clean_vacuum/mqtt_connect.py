"""MQTT connection handler for Eufy Clean."""
import logging
import json
from typing import Any, Dict, List, Optional
import time

import paho.mqtt.client as mqtt

from .exceptions import CannotConnect

_LOGGER = logging.getLogger(__name__)

class MQTTConnect:
    """MQTT connection handler."""

    def __init__(self, mqtt_config: Dict[str, Any]) -> None:
        """Initialize MQTT connection."""
        self.mqtt_config = mqtt_config
        self.client = mqtt.Client(
            client_id=f"android-{mqtt_config.get('app_name')}-eufy_android_{mqtt_config.get('user_id')}-{int(time.time())}"
        )
        self.client.username_pw_set(
            username=mqtt_config.get("thing_name"),
        )
        self.client.tls_set(
            cert_reqs=mqtt.ssl.CERT_NONE,
            certfile=None,
            keyfile=None,
            certs_string=mqtt_config.get("certificate_pem"),
            keyfile_password=None,
        )
        self.client.tls_insecure_set(True)
        self.devices = []

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Handle connection established."""
        if rc == 0:
            _LOGGER.debug("Connected to MQTT broker")
            # Subscribe to device status topics
            client.subscribe("device/+/status")
        else:
            _LOGGER.error("Failed to connect to MQTT broker with result code %s", rc)

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Handle disconnection."""
        _LOGGER.warning("Disconnected from MQTT broker with result code %s", rc)

    async def connect(self) -> None:
        """Connect to MQTT broker."""
        try:
            endpoint = self.mqtt_config.get("endpoint_addr", "mqtt.eufylife.com")
            if not endpoint:
                raise CannotConnect("No MQTT endpoint available")

            self.client.connect(
                endpoint,
                port=8883,  # Use TLS port
                keepalive=60
            )
            self.client.loop_start()
            _LOGGER.debug("Successfully connected to MQTT broker")
        except Exception as err:
            _LOGGER.error("Error connecting to MQTT broker: %s", err)
            raise CannotConnect(f"Failed to connect to MQTT broker: {err}")

    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            _LOGGER.debug("Successfully disconnected from MQTT broker")
        except Exception as err:
            _LOGGER.error("Error disconnecting from MQTT broker: %s", err)

    async def get_device_list(self) -> List[Dict[str, Any]]:
        """Get list of devices from MQTT."""
        try:
            # Subscribe to device list topic
            self.client.subscribe("device/list")
            return self.devices
        except Exception as err:
            _LOGGER.error("Error getting device list from MQTT: %s", err)
            return []

    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID."""
        try:
            # Subscribe to device topic
            self.client.subscribe(f"device/{device_id}")
            device = next((d for d in self.devices if d.get("device_sn") == device_id), None)
            return device
        except Exception as err:
            _LOGGER.error("Error getting device from MQTT: %s", err)
            return None

    async def send_command(self, device_id: str, dps: Dict[str, Any]) -> None:
        """Send command to device."""
        try:
            # Format command according to original implementation
            payload = {
                "head": {
                    "client_id": f"android-{self.mqtt_config.get('app_name')}-eufy_android_{self.mqtt_config.get('user_id')}",
                    "cmd": 65537,
                    "cmd_status": 2,
                    "msg_seq": 1,
                    "seed": "",
                    "sess_id": f"android-{self.mqtt_config.get('app_name')}-eufy_android_{self.mqtt_config.get('user_id')}",
                    "sign_code": 0,
                    "timestamp": int(time.time() * 1000),
                    "version": "1.0.0.1",
                },
                "payload": json.dumps({
                    "account_id": self.mqtt_config.get("user_id"),
                    "data": dps,
                    "device_sn": device_id,
                    "protocol": 2,
                    "t": int(time.time() * 1000),
                })
            }

            # Publish command to device topic
            topic = f"cmd/eufy_home/{device_id}/req"
            self.client.publish(topic, json.dumps(payload))
            _LOGGER.debug("Successfully sent command to device %s: %s", device_id, dps)
        except Exception as err:
            _LOGGER.error("Error sending command to device %s: %s", device_id, err)
            raise CannotConnect(f"Failed to send command to device: {err}")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """Handle received MQTT messages."""
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic == "device/list":
                self.devices = payload.get("devices", [])
            elif msg.topic.startswith("device/"):
                device_id = msg.topic.split("/")[1]
                device_index = next(
                    (i for i, d in enumerate(self.devices) if d.get("device_sn") == device_id),
                    None
                )
                if device_index is not None:
                    self.devices[device_index].update(payload)
                else:
                    self.devices.append(payload)
        except Exception as err:
            _LOGGER.error("Error handling MQTT message: %s", err)
