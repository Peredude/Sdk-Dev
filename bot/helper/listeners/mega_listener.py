from time import time
from secrets import token_hex
from aiofiles.os import makedirs
from asyncio import Lock
from contextlib import suppress

from ... import LOGGER, task_dict, task_dict_lock, mega_client
from ...core.config_manager import Config
from ..ext_utils.status_utils import MirrorStatus
from ..ext_utils.task_manager import (
    check_running_tasks,
    stop_duplicate_check,
    limit_checker,
)
from ..mirror_leech_utils.status_utils.mega_status import MegaDownloadStatus
from ..mirror_leech_utils.status_utils.queue_status import QueueStatus
from ..telegram_helper.message_utils import send_status_message


mega_tasks = {}


async def mega_cleanup():
    if not mega_tasks:
        return
    LOGGER.info("Running Mega Cleanup...")
    mega_tasks.clear()


class MegaAppListener:
    def __init__(self, listener):
        self.listener = listener
        self.gid = token_hex(5)
        self.mega_status = None
        self.name = ""
        self.size = 0
        self._is_cleaned = False
        self._last_time = time()
        self._val_last = 0
        mega_tasks[self.gid] = self.listener.link

    async def download(self, path):
        """Download a single Mega link"""
        try:
            self._login()
            node = mega_client.get_node_from_link(self.listener.link)
            self._set_metadata(node)

            if not await self._pre_checks():
                return

            await makedirs(path, exist_ok=True)
            mega_client.download(node, path)
            await self.listener.on_download_complete()
        except Exception as e:
            if self.listener.is_cancelled:
                return
            LOGGER.error(f"MegaSDK Download Error: {e}")
            await self.listener.on_download_error(str(e))
        finally:
            await self.cleanup()

    async def download_multiple(self, links, path):
        """Download multiple Mega links sequentially"""
        try:
            self._login()
            await makedirs(path, exist_ok=True)

            for link in links:
                if self.listener.is_cancelled:
                    break

                node = mega_client.get_node_from_link(link)
                self._set_metadata(node)

                if not await self._pre_checks():
                    continue

                LOGGER.info(f"Downloading from MegaSDK: {self.name}")
                mega_client.download(node, path)

            if not self.listener.is_cancelled:
                await self.listener.on_download_complete()
        except Exception as e:
            LOGGER.error(f"MegaSDK Multi-Download Error: {e}")
            await self.listener.on_download_error(str(e))
        finally:
            await self.cleanup()

    def _login(self):
        if Config.MEGA_EMAIL and Config.MEGA_PASSWORD:
            mega_client.login(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        else:
            raise Exception("MegaSDK: Credentials Missing! Login required")

    def _set_metadata(self, node):
        self.name = node.get_name()
        self.size = node.get_size()
        self.listener.name = self.name
        self.listener.size = self.size

        self.mega_status = MegaDownloadStatus(
            self.listener, self, self.gid, MirrorStatus.STATUS_DOWNLOAD
        )
        task_dict[self.listener.mid] = self.mega_status

    async def _pre_checks(self):
        msg, button = await stop_duplicate_check(self.listener)
        if msg:
            await self.listener.on_download_error(msg, button)
            return False

        if limit_exceeded := await limit_checker(self.listener):
            await self.listener.on_download_error(limit_exceeded, is_limit=True)
            return False

        added_to_queue, event = await check_running_tasks(self.listener)
        if added_to_queue:
            LOGGER.info(f"Added to Queue/Download: {self.name}")
            async with task_dict_lock:
                task_dict[self.listener.mid] = QueueStatus(
                    self.listener, self.gid, "Dl"
                )
            await self.listener.on_download_start()
            if self.listener.multi <= 1:
                await send_status_message(self.listener.message)
            await event.wait()
            if self.listener.is_cancelled:
                return False

        return True

    async def cleanup(self):
        if self._is_cleaned:
            return
        self._is_cleaned = True
        try:
            LOGGER.info(f"Cleaning up Mega Task: {self.name}")
            if self.gid in mega_tasks:
                del mega_tasks[self.gid]
        except Exception as e:
            LOGGER.error(f"Mega Cleanup Failed: {e}")

    async def cancel_task(self):
        LOGGER.info(f"Cancelling MegaSDK download: {self.name}")
        self.listener.is_cancelled = True
        try:
            node = mega_client.get_node_from_link(self.listener.link)
            mega_client.cancel_transfer(node)
        except Exception as e:
            LOGGER.error(f"MegaSDK Cancel Failed: {e}")
        with suppress(Exception):
            pass
