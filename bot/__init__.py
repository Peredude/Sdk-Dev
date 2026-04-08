# bot/__init__.py

import logging

# Existing imports for your bot...
# from .core.tg_client import TgClient
# from .core.config_manager import Config
# etc.

# MegaSDK async client
from megasdkrestclient import AsyncMegaSdkRestClient

# Global Mega client reference
mega_client = None

# Initialize logging (if not already done elsewhere)
LOGGER = logging.getLogger(__name__)


async def init_clients():
    """
    Initialize external clients (MegaSDK, etc.).
    Call this once during bot startup inside an async context.
    """
    global mega_client
    try:
        mega_client = AsyncMegaSdkRestClient("http://localhost:6090")
        LOGGER.info("MegaSDK async client initialized.")
    except Exception as e:
        LOGGER.error(f"Failed to initialize MegaSDK client: {e}")


async def close_clients():
    """
    Cleanly close external clients on shutdown.
    Prevents unclosed aiohttp sessions/connectors.
    """
    global mega_client
    if mega_client:
        try:
            await mega_client.close()
            LOGGER.info("MegaSDK async client closed.")
        except Exception as e:
            LOGGER.warning(f"Error closing MegaSDK client: {e}")
