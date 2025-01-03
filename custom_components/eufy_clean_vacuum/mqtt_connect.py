"""MQTT connection handler."""
import logging
import time
import json
import ssl
import tempfile
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import paho.mqtt.client as mqtt
from typing import Any, Dict, List, Optional

from .exceptions import CannotConnect

_LOGGER = logging.getLogger(__name__)
_EXECUTOR = ThreadPoolExecutor(max_workers=1)

class MQTTConnect:
    """MQTT connection handler."""

    def __init__(self, mqtt_config: Dict[str, Any]) -> None:
        """Initialize MQTT connection."""
        self.mqtt_config = mqtt_config
        self.client_id = f"android-{mqtt_config.get('app_name')}-eufy_android_{mqtt_config.get('user_id')}-{int(time.time())}"
        _LOGGER.debug("Initializing MQTT client with ID: %s", self.client_id)

        self.client = mqtt.Client(client_id=self.client_id)
        self.client.username_pw_set(username=mqtt_config.get("thing_name"))
        _LOGGER.debug("Using MQTT username: %s", mqtt_config.get("thing_name"))

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_log = self._on_log
        self.client.on_subscribe = self._on_subscribe
        self.client.on_publish = self._on_publish

        self.devices = []
        self.connected = False
        self.device_model = None
        self.device_id = None
        self._tls_configured = False  # Track TLS configuration state

    def _on_log(self, client: mqtt.Client, userdata: Any, level: int, buf: str) -> None:
        """Handle MQTT log messages."""
        _LOGGER.debug("MQTT Log: %s", buf)

    def _on_subscribe(self, client: mqtt.Client, userdata: Any, mid: int, granted_qos: tuple) -> None:
        """Handle subscription confirmations."""
        _LOGGER.info("MQTT Subscription confirmed - Message ID: %s, Granted QoS: %s", mid, granted_qos)

    def _on_publish(self, client: mqtt.Client, userdata: Any, mid: int) -> None:
        """Handle publish confirmations."""
        _LOGGER.debug("MQTT Message published with ID: %s", mid)

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Handle connection established."""
        if rc == 0:
            self.connected = True
            _LOGGER.info("Connected to MQTT broker with flags: %s", flags)

            # Subscribe to response topic
            if self.device_model and self.device_id:
                # Subscribe to command response topic only, as per TypeScript implementation
                topic = f"cmd/eufy_home/{self.device_model}/{self.device_id}/res"
                _LOGGER.info("Subscribing to device-specific topic: %s", topic)
                result, mid = client.subscribe(topic, 0)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    _LOGGER.info("Successfully subscribed to %s with message ID %s", topic, mid)
                else:
                    _LOGGER.warning("Failed to subscribe to %s (Result: %s)", topic, result)
            else:
                _LOGGER.warning("No device model or ID available, cannot subscribe to specific topics")
        else:
            self.connected = False
            _LOGGER.error("Failed to connect to MQTT broker with result code %s", rc)
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized"
            }
            _LOGGER.error("Connection error: %s", error_messages.get(rc, "Unknown error"))

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """Handle incoming MQTT message."""
        try:
            _LOGGER.info("Received MQTT message - Topic: %s", msg.topic)
            _LOGGER.debug("Raw payload: %s", msg.payload.decode())

            # Parse the message
            message_str = msg.payload.decode()
            _LOGGER.debug("Decoded message string: %s", message_str)

            payload = json.loads(message_str)
            _LOGGER.info("Parsed payload: %s", payload)

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

                    # Update device data
                    device_data = {
                        "device_sn": device_id,
                        "deviceName": data.get("deviceName", ""),
                        "deviceModel": self.device_model,
                        "dps": dps,
                        "mqtt": True,
                        "last_update": int(time.time() * 1000)
                    }

                    # Update or create device
                    device = next((d for d in self.devices if d.get("device_sn") == device_id), None)
                    if device:
                        _LOGGER.info("Updating existing device %s with new data", device_id)
                        device.update(device_data)
                    else:
                        _LOGGER.info("Adding new device from MQTT: %s", device_id)
                        self.devices.append(device_data)

                    # Notify coordinator if available
                    if hasattr(self, "coordinator") and self.coordinator:
                        self.coordinator._handle_mqtt_message(device_id, device_data)
                else:
                    _LOGGER.warning("No 'data' field in payload: %s", data)
            else:
                _LOGGER.warning("No 'payload' field in message: %s", payload)

        except json.JSONDecodeError as err:
            _LOGGER.error("Failed to decode MQTT message: %s\nPayload: %s", err, msg.payload.decode())
        except Exception as err:
            _LOGGER.error("Error handling MQTT message: %s\nPayload: %s", err, msg.payload.decode())

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Handle disconnection."""
        self.connected = False
        if rc == 0:
            _LOGGER.info("Cleanly disconnected from MQTT broker")
        else:
            _LOGGER.warning("Unexpectedly disconnected from MQTT broker with result code %s", rc)
            error_messages = {
                1: "Out of memory",
                2: "Protocol error",
                3: "Invalid message",
                4: "Unknown protocol version",
                5: "Socket error",
                6: "Authentication error",
                7: "ACK timeout",
                8: "Not connected",
                9: "Connection lost",
                10: "Connection refused",
                11: "Connection reset"
            }
            _LOGGER.error("Disconnect reason: %s", error_messages.get(rc, "Unknown error"))

    async def connect(self) -> None:
        """Connect to MQTT broker."""
        try:
            endpoint = self.mqtt_config.get("endpoint_addr", "mqtt.eufylife.com")
            if not endpoint:
                raise CannotConnect("No MQTT endpoint available")

            _LOGGER.debug("Connecting to MQTT broker at %s:8883", endpoint)
            _LOGGER.info("Device info for MQTT - Model: %s, ID: %s", self.device_model, self.device_id)

            # Set up TLS only if not already configured
            if not self._tls_configured:
                def setup_tls():
                    _LOGGER.debug("Setting up TLS")
                    # Create temporary files for certificates
                    cert_fd, cert_file = tempfile.mkstemp()
                    key_fd, key_file = tempfile.mkstemp()

                    try:
                        # Write certificate data
                        cert_data = self.mqtt_config.get("certificate_pem", "").encode("utf-8")
                        key_data = self.mqtt_config.get("private_key", "").encode("utf-8")
                        os.write(cert_fd, cert_data)
                        os.write(key_fd, key_data)
                        os.close(cert_fd)
                        os.close(key_fd)

                        # Set up TLS with the certificate files
                        self.client.tls_set(
                            certfile=cert_file,
                            keyfile=key_file,
                            cert_reqs=ssl.CERT_NONE,
                            tls_version=ssl.PROTOCOL_TLS_CLIENT,
                            ciphers=None
                        )
                        self.client.tls_insecure_set(True)
                        self._tls_configured = True
                        _LOGGER.debug("TLS setup completed")
                    finally:
                        # Clean up temporary files
                        try:
                            os.unlink(cert_file)
                            os.unlink(key_file)
                        except Exception as e:
                            _LOGGER.warning("Error cleaning up certificate files: %s", e)

                await asyncio.get_event_loop().run_in_executor(_EXECUTOR, setup_tls)
            else:
                _LOGGER.debug("TLS already configured, skipping setup")

            # Connect in a thread
            def do_connect():
                _LOGGER.debug("Initiating MQTT connection")
                self.client.connect(
                    endpoint,
                    port=8883,  # Use TLS port
                    keepalive=60
                )
                self.client.loop_start()
                _LOGGER.debug("MQTT loop started")

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_connect)
            _LOGGER.debug("Successfully connected to MQTT broker")

            # Add initial device if we have the info
            if self.device_id and self.device_model:
                _LOGGER.info("Adding initial device to list - ID: %s, Model: %s", self.device_id, self.device_model)
                self.devices.append({
                    "device_sn": self.device_id,
                    "deviceName": "",  # Will be updated from MQTT messages
                    "deviceModel": self.device_model,
                    "dps": {},
                    "mqtt": True,
                    "last_update": int(time.time() * 1000)
                })

        except Exception as err:
            _LOGGER.error("Error connecting to MQTT broker: %s", err)
            raise CannotConnect(f"Failed to connect to MQTT broker: {err}")

    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        try:
            def do_disconnect():
                _LOGGER.debug("Stopping MQTT loop")
                self.client.loop_stop()
                _LOGGER.debug("Disconnecting from MQTT broker")
                self.client.disconnect()

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_disconnect)
            _LOGGER.debug("Successfully disconnected from MQTT broker")
        except Exception as err:
            _LOGGER.error("Error disconnecting from MQTT broker: %s", err)

    async def get_device_list(self) -> List[Dict[str, Any]]:
        """Get list of devices from MQTT."""
        return self.devices

    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID."""
        return next((d for d in self.devices if d.get("device_sn") == device_id), None)

    async def send_command(self, device_id: str, dps: Dict[str, Any]) -> None:
        """Send command to device."""
        if not self.device_model:
            _LOGGER.error("Device model not set, cannot send command")
            return

        try:
            payload = {
                "account_id": self.mqtt_config.get("user_id"),
                "data": dps,
                "device_sn": device_id,
                "protocol": 2,
                "t": int(time.time() * 1000),
            }

            mqtt_val = {
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
                "payload": json.dumps(payload),
            }

            def do_publish():
                topic = f"cmd/eufy_home/{self.device_model}/{device_id}/req"
                _LOGGER.debug("Publishing command to topic: %s", topic)
                result = self.client.publish(
                    topic,
                    json.dumps(mqtt_val)
                )
                _LOGGER.debug("Command publish result: %s", result.rc)

            _LOGGER.debug("Sending command to device %s: %s", device_id, payload)
            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_publish)
        except Exception as err:
            _LOGGER.error("Error sending command to device: %s", err)
            raise
    async def set_device_info(self, device_id: str, device_model: str) -> None:
        """Set device information."""
        self.device_id = device_id
        self.device_model = device_model
        _LOGGER.info("Set device info - ID: %s, Model: %s", device_id, device_model)

