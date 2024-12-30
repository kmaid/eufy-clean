"""Eufy Clean API client."""
import logging
import uuid
from typing import Dict, List, Optional

from .controllers.login import EufyLogin

_LOGGER = logging.getLogger(__name__)

class EufyClean:
    """Eufy Clean API client."""

    def __init__(self, username: str, password: str, openudid: Optional[str] = None):
        """Initialize the API client."""
        if not openudid:
            openudid = str(uuid.uuid4())

        self.login = EufyLogin(username, password, openudid)
        self._available = False

    @property
    def available(self) -> bool:
        """Return if the API is available."""
        return self._available

    async def init(self) -> None:
        """Initialize connection and authenticate."""
        try:
            await self.login.init()
            self._available = True
        except Exception as err:
            self._available = False
            raise

    async def close(self) -> None:
        """Close all connections."""
        self._available = False
        await self.login.close()
