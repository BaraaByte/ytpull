# Modern yt-dlp Downloader

A modern Tkinter GUI for yt-dlp with:
- 🖼 Thumbnail + title preview (Unicode-safe, any language)
- 🎬 MP4 / 🎵 MP3 format picker
- 📁 Separate output folders for MP4 and MP3
- 📊 Real progress bar (%, speed, ETA)
- 🧵 Fully non-blocking (all I/O on worker threads)

## Install
```bash
pip install -r requirements.txt
```
You also need ffmpeg on your PATH (for MP4 merging and MP3 conversion).

## Run
```bash
python main.py
```

## Structure
```text
main.py          — entry point
app/theme.py     — ttk styling
app/progress.py  — progress formatting
app/downloader.py— yt-dlp wrapper (threaded)
app/ui.py        — Tkinter window
```
