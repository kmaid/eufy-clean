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
        client_id = f"android-{mqtt_config.get('app_name')}-eufy_android_{mqtt_config.get('user_id')}-{int(time.time())}"
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(username=mqtt_config.get("thing_name"))

        # Create temporary files for certificates
        self.cert_file = None
        self.key_file = None

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        self.devices = []

    async def _setup_certificates(self) -> None:
        """Set up certificates for TLS connection."""
        try:
            # Create temporary files for certificates
            cert_data = self.mqtt_config.get("certificate_pem", "").encode("utf-8")
            key_data = self.mqtt_config.get("private_key", "").encode("utf-8")

            # Create temporary files in a thread
            def create_cert_files():
                cert_fd, cert_file = tempfile.mkstemp()
                key_fd, key_file = tempfile.mkstemp()
                os.write(cert_fd, cert_data)
                os.write(key_fd, key_data)
                os.close(cert_fd)
                os.close(key_fd)
                return cert_file, key_file

            self.cert_file, self.key_file = await asyncio.get_event_loop().run_in_executor(
                _EXECUTOR, create_cert_files
            )

            # Set up TLS in a thread
            def setup_tls():
                self.client.tls_set(
                    certfile=self.cert_file,
                    keyfile=self.key_file,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLS,
                    ciphers=None,
                    ca_certs=None  # Use system CA certificates
                )
                self.client.tls_insecure_set(True)

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, setup_tls)

        except Exception as err:
            await self._cleanup_certificate_files()
            raise CannotConnect(f"Failed to set up certificates: {err}")

    async def _cleanup_certificate_files(self) -> None:
        """Clean up temporary certificate files."""
        try:
            def cleanup():
                if self.cert_file and os.path.exists(self.cert_file):
                    os.unlink(self.cert_file)
                if self.key_file and os.path.exists(self.key_file):
                    os.unlink(self.key_file)

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, cleanup)
        except Exception as err:
            _LOGGER.error("Error cleaning up certificate files: %s", err)

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Handle connection established."""
        if rc == 0:
            _LOGGER.debug("Connected to MQTT broker")
            # Subscribe to device status topics
            client.subscribe("device/+/status")
        else:
            _LOGGER.error("Failed to connect to MQTT broker with result code %s", rc)

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """Handle incoming MQTT message."""
        try:
            payload = json.loads(msg.payload.decode())
            _LOGGER.debug("Received message on topic %s: %s", msg.topic, payload)

            if msg.topic == "device/list":
                self.devices = payload.get("devices", [])
            elif msg.topic.startswith("device/"):
                device_id = msg.topic.split("/")[1]
                device = next((d for d in self.devices if d.get("device_sn") == device_id), None)
                if device:
                    device.update(payload)
                else:
                    self.devices.append(payload)
        except Exception as err:
            _LOGGER.error("Error handling MQTT message: %s", err)

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Handle disconnection."""
        _LOGGER.warning("Disconnected from MQTT broker with result code %s", rc)

    async def connect(self) -> None:
        """Connect to MQTT broker."""
        try:
            endpoint = self.mqtt_config.get("endpoint_addr", "mqtt.eufylife.com")
            if not endpoint:
                raise CannotConnect("No MQTT endpoint available")

            # Set up certificates before connecting
            await self._setup_certificates()

            # Connect in a thread
            def do_connect():
                self.client.connect(
                    endpoint,
                    port=8883,  # Use TLS port
                    keepalive=60
                )
                self.client.loop_start()

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_connect)
            _LOGGER.debug("Successfully connected to MQTT broker")
        except Exception as err:
            _LOGGER.error("Error connecting to MQTT broker: %s", err)
            await self._cleanup_certificate_files()
            raise CannotConnect(f"Failed to connect to MQTT broker: {err}")

    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        try:
            def do_disconnect():
                self.client.loop_stop()
                self.client.disconnect()

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_disconnect)
            _LOGGER.debug("Successfully disconnected from MQTT broker")
        except Exception as err:
            _LOGGER.error("Error disconnecting from MQTT broker: %s", err)
        finally:
            await self._cleanup_certificate_files()

    async def get_device_list(self) -> List[Dict[str, Any]]:
        """Get list of devices from MQTT."""
        try:
            # Subscribe to device list topic
            def do_subscribe():
                self.client.subscribe("device/list")

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_subscribe)
            return self.devices
        except Exception as err:
            _LOGGER.error("Error getting device list from MQTT: %s", err)
            return []

    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID."""
        try:
            # Subscribe to device topic
            def do_subscribe():
                self.client.subscribe(f"device/{device_id}")

            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_subscribe)
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
                self.client.publish(
                    f"cmd/eufy_home/{device_id}/req",
                    json.dumps(mqtt_val)
                )

            _LOGGER.debug("Sending command to device %s: %s", device_id, payload)
            await asyncio.get_event_loop().run_in_executor(_EXECUTOR, do_publish)
        except Exception as err:
            _LOGGER.error("Error sending command to device: %s", err)
            raise
