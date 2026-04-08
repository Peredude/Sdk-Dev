# bot/__init__.py

import logging

LOGGER = logging.getLogger(__name__)

# Global Mega client reference
mega_client = None

async def init_clients():
    """
    Initialize MegaSDK async client inside the event loop.
    """
    global mega_client
    from aiohttp import ClientSession
    from megasdkrestclient import AsyncMegaSdkRestClient

    # Create the session inside the running loop
    session = ClientSession()
    mega_client = AsyncMegaSdkRestClient("http://localhost:6090", session=session)
    LOGGER.info("MegaSDK async client initialized.")

async def close_clients():
    """
    Cleanly close MegaSDK client on shutdown.
    """
    global mega_client
    if mega_client:
        try:
            await mega_client.close()
            LOGGER.info("MegaSDK async client closed.")
        except Exception as e:
            LOGGER.warning(f"Error closing MegaSDK client: {e}")
