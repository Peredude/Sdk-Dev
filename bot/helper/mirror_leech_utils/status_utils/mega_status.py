from ...ext_utils.status_utils import (
    EngineStatus,
    get_readable_file_size,
    get_readable_time,
)


class MegaDownloadStatus:
    def __init__(self, listener, obj, gid, status=""):
        self.listener = listener
        self._obj = obj
        self._gid = gid
        self._status = status
        self._speed = 0
        self._downloaded_bytes = 0
        self._size = self.listener.size
        self._nodes = []  # track multiple transfers when multi-link is used
        self.engine = EngineStatus().STATUS_MEGA

    def name(self):
        if getattr(self.listener, "multi", 1) > 1:
            return f"{self.listener.multi} Mega links"
        return self.listener.name

    def progress_raw(self):
        try:
            if self._nodes:
                total_downloaded = sum(n.bytes_transferred for n in self._nodes)
                total_size = sum(n.total_bytes for n in self._nodes)
                return round(total_downloaded / total_size * 100, 2)
            return round(self._downloaded_bytes / self._size * 100, 2)
        except ZeroDivisionError:
            return 0.0

    def progress(self):
        return f"{self.progress_raw()}%"

    def status(self):
        return self._status

    def processed_bytes(self):
        if self._nodes:
            total_downloaded = sum(n.bytes_transferred for n in self._nodes)
            return get_readable_file_size(total_downloaded)
        return get_readable_file_size(self._downloaded_bytes)

    def eta(self):
        try:
            if self._nodes:
                total_size = sum(n.total_bytes for n in self._nodes)
                total_downloaded = sum(n.bytes_transferred for n in self._nodes)
                total_speed = sum(n.speed for n in self._nodes)
                seconds = (total_size - total_downloaded) / total_speed
                return get_readable_time(seconds)
            seconds = (self._size - self._downloaded_bytes) / self._speed
            return get_readable_time(seconds)
        except ZeroDivisionError:
            return "-"

    def size(self):
        if self._nodes:
            total_size = sum(n.total_bytes for n in self._nodes)
            return get_readable_file_size(total_size)
        return get_readable_file_size(self._size)

    def speed(self):
        if self._nodes:
            total_speed = sum(n.speed for n in self._nodes)
            return f"{get_readable_file_size(total_speed)}/s"
        return f"{get_readable_file_size(self._speed)}/s"

    def gid(self):
        return self._gid

    def task(self):
        return self

    async def cancel_task(self):
        await self._obj.cancel_task()
        await self.listener.on_download_error(f"{self._status} stopped by user!")
