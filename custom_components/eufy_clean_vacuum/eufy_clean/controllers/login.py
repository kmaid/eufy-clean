"""Login controller for Eufy Clean."""
import logging
import aiohttp
import async_timeout
import hashlib

from ...exceptions import InvalidAuth, CannotConnect

_LOGGER = logging.getLogger(__name__)

class EufyLogin:
    """Handle login to Eufy Clean API."""

    def __init__(self, username: str, password: str, openudid: str):
        """Initialize login controller."""
        self.username = username
        self.password = password
        self.openudid = openudid
        self._session = None
        self.session_data = None
        self.user_info = None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the current session or create a new one."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def init(self) -> None:
        """Initialize connection and authenticate."""
        try:
            await self.login()
            await self.get_user_info()  # Get user info before device lists

            # After successful login and user info, get devices
            cloud_devices = await self.get_cloud_device_list()
            mqtt_devices = await self.get_device_list()

            _LOGGER.info("Found %d cloud devices and %d MQTT devices",
                        len(cloud_devices) if cloud_devices else 0,
                        len(mqtt_devices) if mqtt_devices else 0)

            if cloud_devices:
                for device in cloud_devices:
                    _LOGGER.debug("Cloud device: %s", device)
            if mqtt_devices:
                for device in mqtt_devices:
                    _LOGGER.debug("MQTT device: %s", device)

        except Exception as err:
            _LOGGER.error("Error during authentication: %s", str(err))
            await self.close()
            raise

    async def get_user_info(self) -> None:
        """Get user information."""
        url = "https://api.eufylife.com/v1/user/user_center_info"

        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "EufyHome-Android-3.1.3-753",
            "timezone": "Europe/Berlin",
            "category": "Home",
            "token": self.session_data["access_token"],
            "openudid": self.openudid,
            "clienttype": "2",
            "language": "de",
            "country": "DE",
        }

        try:
            async with self.session.get(url, headers=headers) as response:
                data = await response.json()
                self.user_info = data

                if not data.get("user_center_id"):
                    _LOGGER.error("No user_center_id found")
                    return

                # Create gtoken like the original implementation
                self.user_info["gtoken"] = hashlib.md5(
                    data["user_center_id"].encode()
                ).hexdigest()

                _LOGGER.debug("Got user info successfully")
        except Exception as err:
            _LOGGER.error("Failed to get user info: %s", err)
            raise

    async def login(self) -> None:
        """Perform login to Eufy."""
        url = "https://home-api.eufylife.com/v1/user/email/login"

        headers = {
            "category": "Home",
            "Accept": "*/*",
            "openudid": self.openudid,
            "Accept-Language": "nl-NL;q=1, uk-DE;q=0.9, en-NL;q=0.8",
            "Content-Type": "application/json",
            "clientType": "1",
            "language": "nl",
            "User-Agent": "EufyHome-iOS-2.14.0-6",
            "timezone": "Europe/Berlin",
            "country": "NL",
            "Connection": "keep-alive"
        }

        payload = {
            "email": self.username,
            "password": self.password,
            "client_id": "eufyhome-app",
            "client_secret": "GQCpr9dSp3uQpsOMgJ4xQ"
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()
                    _LOGGER.debug("Auth response: %s", data)

                    if data and data.get("access_token"):
                        _LOGGER.debug("Login successful")
                        self.session_data = data  # Store the entire response like the original
                        return

                    # Handle specific error codes from the API
                    error_code = data.get("res_code")
                    message = data.get("message", "Unknown error")

                    if error_code == 5002:
                        _LOGGER.error("Invalid credentials: %s", message)
                        raise InvalidAuth("Invalid email or password")
                    elif error_code == 0 and "Password length" in message:
                        _LOGGER.error("Password length error: %s", message)
                        raise InvalidAuth("Password must be at least 6 characters")

                    _LOGGER.error("Login failed: %s", data)
                    raise CannotConnect("Failed to authenticate with Eufy")

        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to connect to Eufy: %s", err)
            raise CannotConnect("Connection error") from err
        except InvalidAuth:
            raise
        except Exception as err:
            _LOGGER.error("Error during login: %s", err)
            raise CannotConnect("Unexpected error") from err

    async def get_cloud_device_list(self) -> list:
        """Get list of devices from Eufy Cloud API."""
        url = "https://api.eufylife.com/v1/device/v2"

        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "EufyHome-Android-3.1.3-753",
            "timezone": "Europe/Berlin",
            "category": "Home",
            "token": self.session_data["access_token"],
            "openudid": self.openudid,
            "clienttype": "2",
            "language": "nl",
            "country": "NL",
        }

        try:
            async with self.session.get(url, headers=headers) as response:
                data = await response.json()

                if data.get("data"):
                    data = data["data"]

                if data.get("devices"):
                    return data["devices"]
                return []
        except Exception as err:
            _LOGGER.error("Failed to get cloud device list: %s", err)
            return []

    async def get_device_list(self) -> list:
        """Get list of devices from MQTT API."""
        if not self.user_info:
            _LOGGER.error("No user info available for MQTT device list")
            return []

        url = "https://aiot-clean-api-pr.eufylife.com/app/devicerelation/get_device_list"

        headers = {
            "user-agent": "EufyHome-Android-3.1.3-753",
            "timezone": "Europe/Berlin",
            "openudid": self.openudid,
            "language": "de",
            "country": "DE",
            "os-version": "Android",
            "model-type": "PHONE",
            "app-name": "eufy_home",
            "x-auth-token": self.user_info.get("user_center_token"),
            "gtoken": self.user_info.get("gtoken"),
            "content-type": "application/json; charset=UTF-8",
        }

        payload = {"attribute": 3}

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                data = await response.json()
                _LOGGER.debug("MQTT device list response: %s", data)

                if data.get("data"):
                    data = data["data"]

                device_array = []
                if data.get("devices"):
                    for device_object in data["devices"]:
                        if "device" in device_object:
                            device_array.append(device_object["device"])

                return device_array
        except Exception as err:
            _LOGGER.error("Failed to get MQTT device list: %s", err)
            return []

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
