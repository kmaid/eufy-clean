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

    async def init(self) -> None:
        """Initialize connection and authenticate."""
        await self.login.init()

    async def close(self) -> None:
        """Close all connections."""
        await self.login.close()
