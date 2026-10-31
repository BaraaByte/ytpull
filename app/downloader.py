"""yt-dlp wrapper. All network work happens in worker threads and reports
back to the UI through callbacks (never touches Tk directly)."""
import io
import os
import threading
import urllib.request

from PIL import Image
import yt_dlp

from .progress import build_progress_text


class DownloadJob:
    """
    Handles fetching metadata and downloading a single URL.
    Callbacks are invoked from the worker thread; the caller is responsible
    for marshalling them to the UI thread (e.g. via root.after).
    """

    def __init__(self, url, on_info, on_error):
        self.url = url
        self.on_info = on_info      # (info: dict, title: str, thumb: PIL.Image|None)
        self.on_error = on_error    # (message: str)

    # ------------- metadata -------------
    def fetch_info_async(self):
        threading.Thread(target=self._fetch_info, daemon=True).start()

    def _fetch_info(self):
        try:
            with yt_dlp.YoutubeDL(
                {"quiet": True, "no_warnings": True, "skip_download": True}
            ) as ydl:
                info = ydl.extract_info(self.url, download=False)

            title = info.get("title", "Unknown Title")
            thumb_url = info.get("thumbnail")

            thumb_img = None
            if thumb_url:
                try:
                    req = urllib.request.Request(
                        thumb_url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        raw = resp.read()
                    thumb_img = Image.open(io.BytesIO(raw))
                except Exception:
                    thumb_img = None

            self.on_info(info, title, thumb_img)
        except Exception as e:
            self.on_error(str(e))

    # ------------- download -------------
    def download_async(self, target_dir, fmt, on_progress, on_done, on_error):
        threading.Thread(
            target=self._download,
            args=(target_dir, fmt, on_progress, on_done, on_error),
            daemon=True,
        ).start()

    def _download(self, target_dir, fmt, on_progress, on_done, on_error):
        try:
            os.makedirs(target_dir, exist_ok=True)
            outtmpl = os.path.join(target_dir, "%(title)s.%(ext)s")

            if fmt == "mp3":
                opts = {
                    "format": "bestaudio/best",
                    "outtmpl": outtmpl,
                    "quiet": True, "no_warnings": True, "noprogress": True,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                }
            else:  # mp4
                opts = {
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "outtmpl": outtmpl,
                    "quiet": True, "no_warnings": True, "noprogress": True,
                    "merge_output_format": "mp4",
                }

            def _hook(d):
                if d.get("status") == "downloading":
                    percent, text = build_progress_text(d)
                    on_progress(percent, text)
                elif d.get("status") == "finished":
                    on_progress(100, "Download finished. Converting / merging…")

            opts["progress_hooks"] = [_hook]

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])

            on_done(fmt, target_dir)
        except Exception as e:
            on_error(str(e))
