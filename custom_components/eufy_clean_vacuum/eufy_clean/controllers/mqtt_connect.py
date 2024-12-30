"""MQTT connection controller."""
import asyncio
import json
import logging
from typing import Dict, Optional

import paho.mqtt.client as mqtt

_LOGGER = logging.getLogger(__name__)


class MqttConnect:
    """MQTT connection controller."""

    def __init__(self, mqtt_config: Dict):
        """Initialize MQTT connection.

        Args:
            mqtt_config: MQTT configuration
                Required keys:
                - host: MQTT broker hostname
                - port: MQTT broker port
                - username: MQTT username
                - password: MQTT password
        """
        self.mqtt_config = mqtt_config
        self.client = mqtt.Client()
        self.client.username_pw_set(
            mqtt_config["username"],
            mqtt_config["password"]
        )
        self.connected = False
        self.device_status = {}

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection established."""
        _LOGGER.info("Connected to MQTT broker with result code %s", rc)
        self.connected = True

        # Subscribe to device status topics
        client.subscribe("device/+/status")

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT message."""
        try:
            # Extract device SN from topic
            device_sn = msg.topic.split('/')[1]
            payload = json.loads(msg.payload.decode())
            self.device_status[device_sn] = payload
            _LOGGER.debug("Received status for device %s: %s", device_sn, payload)
        except Exception as err:
            _LOGGER.error("Failed to process MQTT message: %s", err)

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        _LOGGER.warning("Disconnected from MQTT broker with result code %s", rc)
        self.connected = False

    async def connect(self) -> None:
        """Connect to MQTT broker."""
        try:
            self.client.connect(
                self.mqtt_config["host"],
                self.mqtt_config["port"],
                60
            )
            self.client.loop_start()

            # Wait for connection
            for _ in range(10):
                if self.connected:
                    break
                await asyncio.sleep(1)

            if not self.connected:
                raise Exception("Failed to connect to MQTT broker")

        except Exception as err:
            _LOGGER.error("Failed to connect to MQTT broker: %s", err)
            raise

    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()

    async def send_command(self, device_sn: str, command: Dict) -> None:
        """Send command to device.

        Args:
            device_sn: Device serial number
            command: Command data to send
        """
        if not self.connected:
            raise Exception("Not connected to MQTT broker")

        try:
            topic = f"device/{device_sn}/command"
            payload = json.dumps(command)
            self.client.publish(topic, payload)
            _LOGGER.debug("Sent command to device %s: %s", device_sn, command)
        except Exception as err:
            _LOGGER.error("Failed to send command: %s", err)
            raise

    async def get_device_status(self, device_sn: str) -> Optional[Dict]:
        """Get device status.

        Args:
            device_sn: Device serial number

        Returns:
            Device status data or None if not found
        """
        return self.device_status.get(device_sn)
