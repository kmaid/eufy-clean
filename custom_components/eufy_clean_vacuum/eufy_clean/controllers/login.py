"""Login controller for Eufy Clean."""
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

class EufyLogin:
    """Handle login to Eufy Clean API."""

    def __init__(self, username: str, password: str, openudid: str):
        """Initialize login controller."""
        self.username = username
        self.password = password
        self.openudid = openudid
        self.session = aiohttp.ClientSession()
        self.access_token = None
        self.user_id = None

    async def init(self) -> None:
        """Initialize connection and authenticate."""
        try:
            # Correct authentication endpoint
            url = "https://home-api.eufylife.com/v1/user/email/login"

            # Required headers matching original implementation
            headers = {
                "category": "Home",
                "Accept": "*/*",
                "openudid": self.openudid,
                "Accept-Language": "en-US;q=1",
                "Content-Type": "application/json",
                "clientType": "1",
                "language": "en",
                "User-Agent": "EufyHome-iOS-2.14.0-6",
                "timezone": "America/Los_Angeles",
                "country": "US",
                "Connection": "keep-alive"
            }

            # Auth payload matching original implementation
            payload = {
                "email": self.username,
                "password": self.password,
                "client_id": "eufyhome-app",
                "client_secret": "GQCpr9dSp3uQpsOMgJ4xQ"
            }

            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.error("Authentication failed: %s", await response.text())
                    raise Exception("Failed to authenticate with Eufy")

                data = await response.json()

                if data.get("access_token"):
                    self.access_token = data["access_token"]
                    _LOGGER.debug("Successfully authenticated with Eufy")
                else:
                    _LOGGER.error("Login failed: %s", data)
                    raise Exception("No access token received")

        except Exception as e:
            _LOGGER.error("Error during authentication: %s", str(e))
            await self.close()  # Ensure we close the session on error
            raise

    async def close(self) -> None:
        """Close the session."""
        if not self.session.closed:
            await self.session.close()
