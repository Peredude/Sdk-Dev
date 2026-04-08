import logging
import asyncio
from megasdkrestclient import AsyncMegaSdkRestClient
from aiohttp import ClientSession

LOGGER = logging.getLogger(__name__)

# Global event loop
bot_loop = asyncio.get_event_loop()

# Global Mega client reference
mega_client = None

async def init_clients():
    global mega_client
    session = ClientSession()
    mega_client = AsyncMegaSdkRestClient("http://localhost:6090", session=session)
    LOGGER.info("MegaSDK async client initialized.")

async def close_clients():
    global mega_client
    if mega_client:
        try:
            await mega_client.close()
            LOGGER.info("MegaSDK async client closed.")
        except Exception as e:
            LOGGER.warning(f"Error closing MegaSDK client: {e}")
