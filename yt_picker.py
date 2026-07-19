"""YouTube channel live-stream picker — yt-dlp based, no API key.

Fetches the most recent *past* live streams (was_live broadcasts) from a
configured YouTube channel so the user can pick one by number instead of
copy-pasting a URL. Needs network + yt-dlp; callers should fall back to a
manual URL prompt on failure.
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class LiveStream:
    url: str
    title: str
    duration: Optional[float] = None


def _channel_streams_url(channel: str) -> str:
    """Normalize a handle/id/URL into the channel's /streams tab URL."""
    if channel.startswith("http://") or channel.startswith("https://"):
        return channel
    handle = channel if channel.startswith("@") else f"@{channel}"
    return f"https://www.youtube.com/{handle}/streams"


def _run_yt_dlp_json(url: str, probe: int = 20) -> dict:
    """Run yt-dlp flat-playlist JSON for the first `probe` entries."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "-I", f"1-{probe}",
        "-J",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:500] or "yt-dlp returned non-zero")
    return json.loads(proc.stdout)


def _is_past_live(entry: dict) -> bool:
    if entry.get("live_status") == "was_live":
        return True
    # Older yt-dlp builds expose a was_live boolean instead.
    if entry.get("live_status") is None and entry.get("was_live"):
        return True
    return False


def fetch_live_streams(channel: str, limit: int = 5) -> list[LiveStream]:
    """Return up to `limit` most-recent past live streams from `channel`.

    `channel` is a YT handle (@foo), id, or URL. The /streams tab is
    newest-first; we keep the first `limit` that were live broadcasts.
    """
    url = _channel_streams_url(channel)
    data = _run_yt_dlp_json(url)
    out: list[LiveStream] = []
    for entry in data.get("entries") or []:
        if not _is_past_live(entry):
            continue
        vid = entry.get("id") or entry.get("url")
        if not vid:
            continue
        out.append(LiveStream(
            url=f"https://www.youtube.com/watch?v={vid}",
            title=entry.get("title", ""),
            duration=entry.get("duration"),
        ))
        if len(out) >= limit:
            break
    return out
