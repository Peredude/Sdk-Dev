# bot/__main__.py

from . import LOGGER, bot_loop, init_clients, close_clients
from .core.tg_client import TgClient

async def main():
    # Initialize MegaSDK client
    await init_clients()

    # Start Telegram client
    await TgClient.start()

    # Keep running until stopped
    await TgClient.idle()

    # On shutdown, close MegaSDK client
    await close_clients()

if __name__ == "__main__":
    bot_loop.run_until_complete(main())
