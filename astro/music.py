import asyncio
import threading

class NowPlaying:
    """Hears about song changes straight from Windows (the same media info the
    volume flyout and Wallpaper Engine use). It is event-driven: this thread
    sleeps until Windows says something changed - no polling, ~0% CPU.
    Optional: needs  pip install winrt-runtime winrt-Windows.Media.Control
                     winrt-Windows.Foundation winrt-Windows.Foundation.Collections
                     winrt-Windows.Storage.Streams
    Without it Astro simply doesn't announce music."""

    def __init__(self, callback):
        self.cb, self.last, self.sess, self.timer, self.loop = callback, None, None, None, None
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            try:
                from winrt.windows.media.control import (
                    GlobalSystemMediaTransportControlsSessionManager as Manager)
            except ImportError:
                from winsdk.windows.media.control import (
                    GlobalSystemMediaTransportControlsSessionManager as Manager)
        except ImportError:
            print("Astro: music announcements are off (pip install winrt-runtime "
                  "winrt-Windows.Media.Control winrt-Windows.Foundation "
                  "winrt-Windows.Foundation.Collections winrt-Windows.Storage.Streams)")
            return
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._start(Manager))
            self.loop.run_forever()  # idle until Windows calls us
        except Exception as e:
            print("Astro: music announcements unavailable:", e)

    async def _start(self, Manager):
        self.mgr = await Manager.request_async()
        self._on_session = lambda sender, args: self.loop.call_soon_threadsafe(self._rebind)
        self._on_change = lambda sender, args: self.loop.call_soon_threadsafe(self._schedule)
        self.mgr.add_current_session_changed(self._on_session)
        self._rebind(first=True)
        await self._read(announce=False)  # remember what's already playing, stay quiet

    def _rebind(self, first=False):
        if self.sess is not None:
            try:
                self.sess.remove_media_properties_changed(self.tok1)
                self.sess.remove_playback_info_changed(self.tok2)
            except Exception:
                pass
        try:
            self.sess = self.mgr.get_current_session()
        except Exception:
            self.sess = None
        if self.sess is not None:
            self.tok1 = self.sess.add_media_properties_changed(self._on_change)
            self.tok2 = self.sess.add_playback_info_changed(self._on_change)
        if not first:
            self._schedule()

    def _schedule(self):  # wait a moment: players fire several half-filled updates per song
        if self.timer:
            self.timer.cancel()
        self.timer = self.loop.call_later(
            1.0, lambda: asyncio.ensure_future(self._read(), loop=self.loop))

    async def _read(self, announce=True):
        s = self.sess
        if s is None:
            return
        try:
            if int(s.get_playback_info().playback_status) != 4:  # 4 = playing
                return
            info = await s.try_get_media_properties_async()
            title, artist = (info.title or "").strip(), (info.artist or "").strip()
        except Exception:
            return
        if not title or (title, artist) == self.last:
            return
        self.last = (title, artist)
        if announce:
            self.cb(title, artist)

