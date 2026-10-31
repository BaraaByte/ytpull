"""Tkinter UI. Owns layout + user interaction only, delegating all network
work to DownloadJob and marshalling worker callbacks via root.after."""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import ImageTk

from .theme import apply_modern_theme
from .downloader import DownloadJob


class ModernDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern yt-dlp Downloader")
        self.root.geometry("760x720")
        self.root.minsize(680, 660)
        apply_modern_theme(root)

        # State
        self.mp4_path = tk.StringVar(value="")
        self.mp3_path = tk.StringVar(value="")
        self.format_choice = tk.StringVar(value="mp4")
        self.current_info = None
        self.job = None

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        # URL row
        frame_url = ttk.Frame(self.root, padding="15 15 15 5")
        frame_url.pack(fill=tk.X)

        ttk.Label(frame_url, text="Video URL:").pack(side=tk.LEFT, padx=(0, 10))
        self.url_entry = ttk.Entry(frame_url, font=("Segoe UI", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self._on_fetch())

        self.btn_fetch = ttk.Button(frame_url, text="Fetch Info", command=self._on_fetch)
        self.btn_fetch.pack(side=tk.RIGHT)

        # Preview row
        frame_preview = ttk.Frame(self.root, padding="15 5")
        frame_preview.pack(fill=tk.BOTH, expand=True)

        self.lbl_thumb = ttk.Label(frame_preview, text="No Thumbnail", anchor="center")
        self.lbl_thumb.pack(pady=(0, 10))

        self.lbl_title = ttk.Label(
            frame_preview, text="Title will appear here...",
            wraplength=700, justify="center", style="Title.TLabel",
        )
        self.lbl_title.pack(pady=5)

        # Format selector
        frame_format = ttk.Frame(self.root, padding="15 5")
        frame_format.pack(fill=tk.X)

        ttk.Label(frame_format, text="Download as:").pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(
            frame_format, text="🎬 MP4 (Video)",
            variable=self.format_choice, value="mp4",
            command=self._on_format_change,
        ).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(
            frame_format, text="🎵 MP3 (Audio)",
            variable=self.format_choice, value="mp3",
            command=self._on_format_change,
        ).pack(side=tk.LEFT)

        # Separate output folders
        folders_box = ttk.LabelFrame(self.root, text="Output folders", padding="10 10 10 10")
        folders_box.pack(fill=tk.X, padx=15, pady=(5, 5))

        row1 = ttk.Frame(folders_box)
        row1.pack(fill=tk.X, pady=3)
        ttk.Label(row1, text="🎬 MP4:", width=10).pack(side=tk.LEFT)
        ttk.Label(row1, textvariable=self.mp4_path, relief="sunken",
                  anchor="w", padding=5, style="Path.TLabel"
                  ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(row1, text="Browse MP4…",
                   command=lambda: self._pick_folder("mp4")).pack(side=tk.RIGHT)

        row2 = ttk.Frame(folders_box)
        row2.pack(fill=tk.X, pady=3)
        ttk.Label(row2, text="🎵 MP3:", width=10).pack(side=tk.LEFT)
        ttk.Label(row2, textvariable=self.mp3_path, relief="sunken",
                  anchor="w", padding=5, style="Path.TLabel"
                  ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(row2, text="Browse MP3…",
                   command=lambda: self._pick_folder("mp3")).pack(side=tk.RIGHT)

        # Download button
        frame_dl = ttk.Frame(self.root, padding="15 10 15 5")
        frame_dl.pack(fill=tk.X)

        self.btn_download = ttk.Button(
            frame_dl, text="Download", command=self._on_download, state=tk.DISABLED,
        )
        self.btn_download.pack(fill=tk.X, ipady=5)

        # Progress
        self.progress = ttk.Progressbar(
            self.root, orient=tk.HORIZONTAL, mode="determinate", maximum=100,
            style="Download.Horizontal.TProgressbar",
        )
        self.progress.pack(fill=tk.X, padx=15, pady=(10, 4))

        self.lbl_status = ttk.Label(self.root, text="Idle", anchor="w", style="Status.TLabel")
        self.lbl_status.pack(fill=tk.X, padx=15, pady=(0, 15))

    # ---------------- Folder ----------------
    def _pick_folder(self, kind):
        folder = filedialog.askdirectory(title=f"Choose {kind.upper()} output folder")
        if not folder:
            return
        if kind == "mp4":
            self.mp4_path.set(os.path.join(folder, "MP4"))
            if not self.mp3_path.get():
                self.mp3_path.set(os.path.join(folder, "MP3"))
        else:
            self.mp3_path.set(os.path.join(folder, "MP3"))
            if not self.mp4_path.get():
                self.mp4_path.set(os.path.join(folder, "MP4"))
        self._refresh_download_button()

    def _current_target(self):
        return self.mp3_path.get() if self.format_choice.get() == "mp3" else self.mp4_path.get()

    def _on_format_change(self):
        self._refresh_download_button()

    def _refresh_download_button(self):
        ready = bool(self.current_info) and bool(self._current_target())
        kind = "MP3" if self.format_choice.get() == "mp3" else "MP4"
        self.btn_download.config(
            state=tk.NORMAL if ready else tk.DISABLED,
            text=f"Download {kind}",
        )
        if self.current_info:
            self.lbl_status.config(
                text=f"Ready → {self._current_target()}"
                if ready else "Choose a folder for this format."
            )

    # ---------------- Fetch ----------------
    def _on_fetch(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL.")
            return
        self.btn_fetch.config(state=tk.DISABLED, text="Fetching...")
        self.lbl_status.config(text="Fetching video info...")
        self.job = DownloadJob(
            url,
            on_info=lambda info, title, thumb: self.root.after(
                0, self._apply_info, info, title, thumb
            ),
            on_error=lambda msg: self.root.after(0, self._on_fetch_error, msg),
        )
        self.job.fetch_info_async()

    def _apply_info(self, info, title, thumb_img):
        self.current_info = info
        self.lbl_title.config(text=title)  # native Unicode

        if thumb_img is not None:
            try:
                thumb_img.thumbnail((400, 225))
                photo = ImageTk.PhotoImage(thumb_img)
                self.lbl_thumb.config(image=photo, text="")
                self.lbl_thumb.image = photo
            except Exception:
                self.lbl_thumb.config(text="Thumbnail could not be loaded", image="")
        else:
            self.lbl_thumb.config(text="No thumbnail available", image="")

        self.btn_fetch.config(state=tk.NORMAL, text="Fetch Info")
        self._refresh_download_button()

    def _on_fetch_error(self, msg):
        messagebox.showerror("Error", f"Could not fetch video info:\n{msg}")
        self.btn_fetch.config(state=tk.NORMAL, text="Fetch Info")
        self.lbl_status.config(text="Fetch failed.")

    # ---------------- Download ----------------
    def _on_download(self):
        target = self._current_target()
        if not self.current_info or not target or not self.job:
            return

        self.btn_download.config(state=tk.DISABLED, text="Downloading...")
        self.btn_fetch.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.lbl_status.config(text=f"Starting → {target}")

        fmt = self.format_choice.get()
        self.job.download_async(
            target_dir=target,
            fmt=fmt,
            on_progress=lambda p, t: self.root.after(0, self._update_progress, p, t),
            on_done=lambda f, d: self.root.after(0, self._on_download_success, f, d),
            on_error=lambda msg: self.root.after(0, self._on_download_error, msg),
        )

    def _update_progress(self, percent, text):
        self.progress["value"] = max(0, min(100, percent))
        self.lbl_status.config(text=text)

    def _on_download_success(self, fmt, target):
        self.progress["value"] = 100
        ext = "MP3" if fmt == "mp3" else "MP4"
        self.lbl_status.config(text=f"✅ {ext} saved → {target}")
        self.btn_download.config(state=tk.NORMAL)
        self.btn_fetch.config(state=tk.NORMAL)
        self._refresh_download_button()
        messagebox.showinfo("Success", f"{ext} download completed.\n\nSaved to:\n{target}")

    def _on_download_error(self, msg):
        self.lbl_status.config(text="❌ Download failed.")
        self.btn_download.config(state=tk.NORMAL)
        self.btn_fetch.config(state=tk.NORMAL)
        self._refresh_download_button()
        messagebox.showerror("Download Error", msg)
