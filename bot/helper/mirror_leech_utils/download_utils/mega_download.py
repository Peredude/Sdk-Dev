from ...listeners.mega_listener import MegaAppListener


async def add_mega_download(listener, path):
    mega_listener = MegaAppListener(listener)

    if hasattr(listener, "links") and listener.multi > 1:
        await mega_listener.download_multiple(listener.links, path)
    else:
        await mega_listener.download(path)
