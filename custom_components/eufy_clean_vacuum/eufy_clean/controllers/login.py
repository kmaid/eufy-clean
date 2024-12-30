import requests
import json
from typing import Dict, List, Optional, Any
import hashlib


def pretty_print(data: Any) -> None:
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


class EufyLogin:
    def __init__(self, username: str, password: str, openudid: str):
        """Initialize Eufy login controller.

        Args:
            username: Eufy account email
            password: Eufy account password
            openudid: Unique device identifier
        """
        self.username = username
        self.password = password
        self.openudid = openudid
        self.session: Optional[Dict] = None
        self.user_info: Optional[Dict] = None
        self.cloud_devices: List = []
        self.mqtt_devices: List = []

    async def init(self) -> None:
        """Initialize connection and fetch device lists."""
        try:
            login_result = await self.login()
            if not login_result:
                raise Exception("Failed to login to Eufy")

            self.cloud_devices = await self.get_cloud_device_list()
            self.mqtt_devices = await self.get_device_list()
        except Exception as error:
            raise Exception(f"Init failed: {error}")

    async def login(self) -> Dict:
        """Perform full login process.

        Returns:
            Dict containing session, user info and MQTT credentials
        """
        try:
            session = await self.eufy_login()
            if not session:
                raise Exception("Failed to login to Eufy")

            user = await self.get_user_info()
            if not user:
                raise Exception("Failed to get user info")

            mqtt = await self.get_mqtt_credentials()
            result = {'session': session, 'user': user, 'mqtt': mqtt}
            print("Login result:")
            pretty_print(result)
            return result
        except Exception as error:
            raise Exception(f"Login failed: {error}")

    async def soft_login(self) -> Dict:
        """Perform minimal login process.

        Returns:
            Dict containing session info
        """
        session = await self.eufy_login()
        result = {'session': session}
        print("Soft login result:")
        pretty_print(result)
        return result

    async def eufy_login(self) -> Optional[Dict]:
        """Login to Eufy account.

        Returns:
            Session info or None if failed
        """
        try:
            response = requests.post(
                'https://home-api.eufylife.com/v1/user/email/login',
                headers={
                    'category': 'Home',
                    'Accept': '*/*',
                    'openudid': self.openudid,
                    'Accept-Language': 'nl-NL;q=1, uk-DE;q=0.9, en-NL;q=0.8',
                    'Content-Type': 'application/json',
                    'clientType': '1',
                    'language': 'nl',
                    'User-Agent': 'EufyHome-iOS-2.14.0-6',
                    'timezone': 'Europe/Berlin',
                    'country': 'NL',
                    'Connection': 'keep-alive',
                },
                json={
                    'email': self.username,
                    'password': self.password,
                    'client_id': 'eufyhome-app',
                    'client_secret': 'GQCpr9dSp3uQpsOMgJ4xQ',
                }
            )

            data = response.json()
            if data and data.get('access_token'):
                self.session = data
                print("Login response:")
                pretty_print(data)
                return data
            print("Login failed:")
            pretty_print(data)
            return None

        except Exception:
            return None

    async def get_cloud_device_list(self) -> List:
        """Get list of cloud-connected devices.

        Returns:
            List of cloud devices
        """
        try:
            response = requests.get(
                'https://api.eufylife.com/v1/device/v2',
                headers={
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'user-agent': 'EufyHome-Android-3.1.3-753',
                    'timezone': 'Europe/Berlin',
                    'category': 'Home',
                    'token': self.session['access_token'],
                    'openudid': self.openudid,
                    'clienttype': '2',
                    'language': 'nl',
                    'country': 'NL',
                }
            )

            data = response.json()
            print("Cloud device list response:")
            pretty_print(data)

            if data.get('data'):
                data = data['data']

            devices = data.get('devices', [])
            print(f"Found {len(devices)} cloud devices")
            return devices

        except Exception:
            return []

    async def get_device_list(self, device_sn: Optional[str] = None) -> List:
        """Get list of MQTT-connected devices.

        Args:
            device_sn: Optional device serial number to filter by

        Returns:
            List of MQTT devices
        """
        if not self.user_info:
            return []

        try:
            response = requests.post(
                'https://aiot-clean-api-pr.eufylife.com/app/devicerelation/get_device_list',
                headers={
                    'user-agent': 'EufyHome-Android-3.1.3-753',
                    'timezone': 'Europe/Berlin',
                    'openudid': self.openudid,
                    'language': 'de',
                    'country': 'DE',
                    'os-version': 'Android',
                    'model-type': 'PHONE',
                    'app-name': 'eufy_home',
                    'x-auth-token': self.user_info['user_center_token'],
                    'gtoken': self.user_info['gtoken'],
                    'content-type': 'application/json; charset=UTF-8',
                },
                json={'attribute': 3}
            )

            data = response.json()
            print("MQTT device list response:")
            pretty_print(data)

            device_array = []

            if data.get('data'):
                data = data['data']

            if data.get('devices'):
                for device_object in data['devices']:
                    device_array.append(device_object['device'])

                if device_sn:
                    matching_device = next((d for d in device_array if d.get('device_sn') == device_sn), None)
                    return [matching_device] if matching_device else []

            print(f"Found {len(device_array)} MQTT devices")
            return device_array

        except Exception:
            return []

    async def get_device_properties(self, device_model: str) -> None:
        """Get device properties.

        Args:
            device_model: Device model identifier
        """
        if not self.user_info:
            return

        try:
            response = requests.post(
                'https://aiot-clean-api-pr.eufylife.com/app/things/get_product_data_point',
                headers={
                    'user-agent': 'EufyHome-Android-3.1.3-753',
                    'timezone': 'Europe/Berlin',
                    'openudid': self.openudid,
                    'language': 'de',
                    'country': 'DE',
                    'os-version': 'Android',
                    'model-type': 'PHONE',
                    'app-name': 'eufy_home',
                    'x-auth-token': self.user_info['user_center_token'],
                    'gtoken': self.user_info['gtoken'],
                    'content-type': 'application/json; charset=UTF-8',
                },
                json={'code': device_model}
            )

            data = response.json()
            print("Device properties response:")
            pretty_print(data)
            return data

        except Exception:
            return None

    async def get_mqtt_credentials(self) -> Optional[Dict]:
        """Get MQTT connection credentials.

        Returns:
            Dictionary containing MQTT credentials or None if failed
        """
        if not self.session or not self.user_info:
            return None

        try:
            response = requests.post(
                'https://aiot-clean-api-pr.eufylife.com/app/devicemanage/get_user_mqtt_info',
                headers={
                    'user-agent': 'EufyHome-Android-3.1.3-753',
                    'timezone': 'Europe/Berlin',
                    'openudid': self.openudid,
                    'language': 'de',
                    'country': 'DE',
                    'os-version': 'Android',
                    'model-type': 'PHONE',
                    'app-name': 'eufy_home',
                    'x-auth-token': self.user_info['user_center_token'],
                    'gtoken': self.user_info['gtoken'],
                    'content-type': 'application/json; charset=UTF-8',
                }
            )

            data = response.json()
            print("MQTT credentials response:")
            pretty_print(data)

            if not data or 'data' not in data:
                return None

            mqtt_config = data['data']
            result = {
                'host': mqtt_config.get('mqtt_host', 'mqtt.eufylife.com'),
                'port': mqtt_config.get('mqtt_port', 1883),
                'username': mqtt_config.get('mqtt_user', ''),
                'password': mqtt_config.get('mqtt_passwd', '')
            }
            print("MQTT config:")
            pretty_print(result)
            return result

        except Exception:
            return None

    async def get_user_info(self) -> Optional[Dict]:
        """Get user information.

        Returns:
            Dictionary containing user info or None if failed
        """
        if not self.session:
            return None

        try:
            response = requests.get(
                'https://api.eufylife.com/v1/user/user_center_info',
                headers={
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'user-agent': 'EufyHome-Android-3.1.3-753',
                    'timezone': 'Europe/Berlin',
                    'category': 'Home',
                    'token': self.session['access_token'],
                    'openudid': self.openudid,
                    'clienttype': '2',
                    'language': 'de',
                    'country': 'DE',
                }
            )

            data = response.json()
            print("User info response:")
            pretty_print(data)

            if not data or not data.get('user_center_id'):
                return None

            gtoken = hashlib.md5(data['user_center_id'].encode()).hexdigest()
            data['gtoken'] = gtoken
            data['user_center_token'] = data.get('user_center_token', self.session['access_token'])

            self.user_info = data
            return self.user_info

        except Exception:
            return None

    async def get_cloud_device(self, device_id: str) -> Optional[Dict]:
        """Get cloud device by ID.

        Args:
            device_id: Device ID to look up

        Returns:
            Device information or None if not found
        """
        devices = await self.get_cloud_device_list()
        device = next((d for d in devices if d.get('device_id') == device_id), None)
        if device:
            print("Found cloud device:")
            pretty_print(device)
        return device

    async def send_cloud_command(self, device_id: str, command: Dict) -> None:
        """Send command to cloud device.

        Args:
            device_id: Target device ID
            command: Command data to send
        """
        if not self.session:
            return

        try:
            print(f"Sending command to device {device_id}:")
            pretty_print(command)

            response = requests.post(
                f'https://api.eufylife.com/v1/device/execute/{device_id}',
                headers={
                    'content-type': 'application/json',
                    'user-agent': 'EufyHome-Android-3.1.3-753',
                    'timezone': 'Europe/Berlin',
                    'category': 'Home',
                    'token': self.session['access_token'],
                    'openudid': self.openudid,
                    'clienttype': '2',
                    'language': 'nl',
                    'country': 'NL',
                },
                json=command
            )

            data = response.json()
            print("Command response:")
            pretty_print(data)

            if not data.get('success'):
                raise Exception('Command failed')

        except Exception:
            return
