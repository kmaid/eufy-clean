"""Eufy Clean login controller."""
import logging
import json
import hashlib
import aiohttp
import async_timeout
import time
from typing import Any, Dict, List, Optional

from .mqtt_connect import MQTTConnect
from .exceptions import InvalidAuth, CannotConnect

_LOGGER = logging.getLogger(__name__)

class EufyLogin:
    """Eufy Clean login controller."""

    def __init__(self, username: str, password: str, openudid: str, locale: str = "en") -> None:
        """Initialize the login controller."""
        self.username = username
        self.password = password
        self.openudid = openudid
        self.locale = locale
        self.session = aiohttp.ClientSession()
        self.user_info = None
        self.cloud_devices = []
        self.mqtt_devices = []
        self.mqtt_credentials = None
        self.mqtt_connect = None

    async def init(self) -> None:
        """Initialize the login process."""
        try:
            await self._login()
            await self._get_user_info()
            await self._get_cloud_devices()
            await self._get_mqtt_credentials()
            await self._connect_mqtt()
            _LOGGER.debug("Successfully initialized login")
        except Exception as err:
            _LOGGER.error("Failed to initialize login: %s", err)
            await self.close()
            raise

    async def _login(self) -> None:
        """Log in to Eufy Clean."""
        url = "https://home-api.eufylife.com/v1/user/email/login"
        headers = {
            "category": "Home",
            "Accept": "*/*",
            "openudid": self.openudid,
            "Accept-Language": f"{self.locale};q=1",
            "Content-Type": "application/json",
            "clientType": "1",
            "language": self.locale.split("-")[0],
            "User-Agent": "EufyHome-iOS-2.14.0-6",
            "timezone": "Europe/Berlin",
            "country": self.locale.split("-")[1] if "-" in self.locale else "US",
            "Connection": "keep-alive",
        }
        payload = {
            "email": self.username,
            "password": self.password,
            "client_id": "eufyhome-app",
            "client_secret": "GQCpr9dSp3uQpsOMgJ4xQ",
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()

                    if not data or not data.get("access_token"):
                        error_msg = "Login failed: " + json.dumps(data)
                        if "password" in str(data).lower():
                            raise InvalidAuth(error_msg)
                        raise CannotConnect(error_msg)

                    self.user_info = data
                    _LOGGER.debug("Successfully logged in")
        except aiohttp.ClientError as err:
            raise CannotConnect(f"Error connecting to API: {err}")
        except Exception as err:
            _LOGGER.error("Error during login: %s", err)
            raise

    async def _get_user_info(self) -> None:
        """Get user information."""
        if not self.user_info:
            raise CannotConnect("No user info available")

        url = "https://api.eufylife.com/v1/user/user_center_info"
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "EufyHome-Android-3.1.3-753",
            "timezone": "Europe/Berlin",
            "category": "Home",
            "token": self.user_info["access_token"],
            "openudid": self.openudid,
            "clienttype": "2",
            "language": self.locale.split("-")[0],
            "country": self.locale.split("-")[1] if "-" in self.locale else "US",
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url, headers=headers) as response:
                    data = await response.json()

                    if not data or not data.get("user_center_id"):
                        raise CannotConnect("Failed to get user info")

                    # Generate gtoken (md5 hash of user_center_id)
                    gtoken = hashlib.md5(data["user_center_id"].encode()).hexdigest()
                    data["gtoken"] = gtoken
                    data["user_center_token"] = data.get("user_center_token", self.user_info["access_token"])

                    self.user_info.update(data)
                    _LOGGER.debug("Successfully got user info")
                    _LOGGER.info("User info retrieved - ID: %s, Email: %s", data.get("user_center_id"), self.username)
        except Exception as err:
            _LOGGER.error("Error getting user info: %s", err)
            raise

    async def _get_cloud_devices(self) -> None:
        """Get cloud devices."""
        if not self.user_info:
            raise CannotConnect("No user info available")

        url = "https://api.eufylife.com/v1/device/v2"
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "EufyHome-Android-3.1.3-753",
            "timezone": "Europe/Berlin",
            "category": "Home",
            "token": self.user_info["access_token"],
            "openudid": self.openudid,
            "clienttype": "2",
            "language": self.locale.split("-")[0],
            "country": self.locale.split("-")[1] if "-" in self.locale else "US",
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url, headers=headers) as response:
                    data = await response.json()
                    _LOGGER.debug("Raw cloud API response: %s", data)

                    if data.get("data"):
                        data = data["data"]
                    self.cloud_devices = data.get("devices", [])
                    _LOGGER.debug("Successfully got cloud devices")

                    # Log detailed cloud device information
                    _LOGGER.info("Found %d cloud devices:", len(self.cloud_devices))
                    transformed_devices = []
                    for device in self.cloud_devices:
                        device_sn = device.get("id")  # This is the device serial number
                        device_name = device.get("name") or device.get("alias_name", "Unknown")
                        device_model = device.get("product", {}).get("name", "Unknown")
                        product_code = device.get("product", {}).get("product_code", "Unknown")

                        _LOGGER.info(
                            "Cloud Device - SN: %s, Name: %s, Model: %s, Product Code: %s",
                            device_sn,
                            device_name,
                            device_model,
                            product_code
                        )
                        _LOGGER.debug("Full cloud device data: %s", device)

                        # Transform cloud device data to match expected format
                        transformed_device = {
                            "device_sn": device_sn,  # Use device_sn consistently
                            "deviceName": device_name,
                            "deviceModel": device_model,
                            "product_code": product_code,
                            "online": not device.get("is_not_work", True),
                            "dps": device.get("dps", {}),
                            "mqtt": False,  # Mark as cloud device
                            "raw_data": device  # Keep original data
                        }
                        transformed_devices.append(transformed_device)

                    # Replace original devices with transformed ones
                    self.cloud_devices = transformed_devices
                    _LOGGER.debug("Transformed cloud devices: %s", self.cloud_devices)
        except Exception as err:
            _LOGGER.error("Error getting cloud devices: %s", err)
            raise

    async def _get_mqtt_credentials(self) -> None:
        """Get MQTT credentials."""
        if not self.user_info:
            raise CannotConnect("No user info available")

        url = "https://aiot-clean-api-pr.eufylife.com/app/devicemanage/get_user_mqtt_info"
        headers = {
            "content-type": "application/json",
            "user-agent": "EufyHome-Android-3.1.3-753",
            "timezone": "Europe/Berlin",
            "openudid": self.openudid,
            "language": self.locale.split("-")[0],
            "country": self.locale.split("-")[1] if "-" in self.locale else "US",
            "os-version": "Android",
            "model-type": "PHONE",
            "app-name": "eufy_home",
            "x-auth-token": self.user_info["user_center_token"],
            "gtoken": self.user_info["gtoken"],
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.post(url, headers=headers) as response:
                    data = await response.json()
                    if data.get("data"):
                        self.mqtt_credentials = data["data"]
                        _LOGGER.debug("Successfully got MQTT credentials")
                        _LOGGER.info(
                            "MQTT credentials retrieved - Endpoint: %s, Thing Name: %s",
                            self.mqtt_credentials.get("endpoint_addr", "Unknown"),
                            self.mqtt_credentials.get("thing_name", "Unknown")
                        )
                    else:
                        raise CannotConnect("Failed to get MQTT credentials")
        except Exception as err:
            _LOGGER.error("Error getting MQTT credentials: %s", err)
            raise

    async def _connect_mqtt(self) -> None:
        """Connect to MQTT broker."""
        try:
            if not self.mqtt_credentials:
                raise CannotConnect("No MQTT credentials available")

            if not self.mqtt_connect:
                _LOGGER.info("Creating new MQTT connection")
                self.mqtt_connect = MQTTConnect(self.mqtt_credentials)
            else:
                _LOGGER.info("Using existing MQTT connection")

            # Get the device model from the cloud device if available
            device_id = None
            device_model = None
            if self.cloud_devices:
                # Get the first cloud device's info
                cloud_device = self.cloud_devices[0]
                device_id = cloud_device.get("device_sn")
                device_model = cloud_device.get("product_code")
                _LOGGER.debug("Using device info from cloud device - ID: %s, Model: %s", device_id, device_model)

            # Set device info if available
            if device_id and device_model:
                _LOGGER.info("Setting device info for MQTT - ID: %s, Model: %s", device_id, device_model)
                await self.mqtt_connect.set_device_info(device_id, device_model)

            # Connect to MQTT
            await self.mqtt_connect.connect()
            _LOGGER.debug("MQTT connect successful")

        except Exception as err:
            _LOGGER.error("Error connecting to MQTT: %s", err)
            raise

    async def get_mqtt_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get MQTT device by ID."""
        if not self.mqtt_connect:
            return None
        return await self.mqtt_connect.get_device(device_id)

    async def send_command(self, device_id: str, dps: Dict[str, Any]) -> None:
        """Send command to device."""
        if not self.mqtt_connect:
            raise CannotConnect("No MQTT connection available")
        await self.mqtt_connect.send_command(device_id, dps)

    async def close(self) -> None:
        """Close all connections."""
        if self.mqtt_connect:
            await self.mqtt_connect.disconnect()
        await self.session.close()
