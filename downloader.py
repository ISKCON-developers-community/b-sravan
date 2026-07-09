"""yt-dlp wrapper: YouTube URL → mp3 file on disk.

Returns the downloaded path. Audio is extracted as mp3 @ 192k, the original
video title is sanitised for filesystem use, and downloads land in
`config.DOWNLOADS_DIR` (created if missing).
"""
from dataclasses import dataclass
from pathlib import Path
import re
import yt_dlp

from config import AUDIO_BITRATE, DOWNLOADS_DIR


@dataclass
class Download:
    path: Path       # absolute path to the .mp3
    title: str       # original video title (used for tag pre-fill)


# Filesystem-unsafe chars → '_'. Keeps Unicode (Cyrillic) intact.
_SAFE_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _safe_filename(title: str) -> str:
    cleaned = _SAFE_RE.sub("_", title).strip(" .")
    return cleaned or "audio"


def download(url: str) -> Download:
    """Download audio from `url` as 192k mp3 into DOWNLOADS_DIR.

    Raises yt_dlp.utils.DownloadError on bad URLs / network errors /
    unsupported sites. Caller is responsible for user-facing messaging.
    """
    out_dir = DOWNLOADS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # First pass: grab the video title (no download, no disk write).
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:  # type: ignore[arg-type]
        info = ydl.extract_info(url, download=False)
    title = info.get("title") or "audio"
    out_template = str(out_dir / f"{_safe_filename(title)}.%(ext)s")

    # Second pass: download + extract audio.
    ydl_opts = {  # type: ignore[var-annotated]
        "quiet": True,
        "no_warnings": True,
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": str(AUDIO_BITRATE),
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    mp3_path = out_dir / f"{_safe_filename(title)}.mp3"
    if not mp3_path.is_file():
        # yt-dlp occasionally picks a different ext when transcoding fails;
        # fall back to whatever landed in the dir matching the title prefix.
        candidates = list(out_dir.glob(f"{_safe_filename(title)}.*"))
        if not candidates:
            raise FileNotFoundError(
                f"yt-dlp finished but no file found for {title!r} in {out_dir}"
            )
        mp3_path = candidates[0]
    return Download(path=mp3_path.resolve(), title=title)
