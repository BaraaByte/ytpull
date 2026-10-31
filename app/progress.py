"""Formatting helpers for the progress bar and status text."""


def fmt_bytes(n):
    if not n:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def fmt_time(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def build_progress_text(d):
    """Given a yt-dlp progress dict, return (percent, human_text)."""
    total = d.get("total_bytes") or d.get("total_bytes_estimate")
    downloaded = d.get("downloaded_bytes", 0)
    percent = (downloaded / total * 100) if total else 0

    speed = d.get("speed") or 0
    eta = d.get("eta")
    speed_str = f"{fmt_bytes(speed)}/s" if speed else "—"
    eta_str = fmt_time(eta) if eta is not None else "—"

    text = (
        f"Downloading… {percent:5.1f}%  |  "
        f"{fmt_bytes(downloaded)} / {fmt_bytes(total) if total else '?'}  |  "
        f"Speed: {speed_str}  |  ETA: {eta_str}"
    )
    return percent, text
