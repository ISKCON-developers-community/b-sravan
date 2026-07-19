"""YouTube channel live-stream picker — yt-dlp based, no API key.

Fetches the most recent streams from a configured YouTube channel so the
user can pick one by number instead of copy-pasting a URL.

Proven approach (mirrors ~/.hermes/scripts/soznanie_streams_msg.py, which
runs daily via cron for this channel):
  - use the channel's /streams tab (newest-first live archive)
  - --extractor-args youtube:lang=ru to keep the uploader's ORIGINAL
    Russian titles (the /streams tab otherwise returns YouTube
    auto-translated English titles for some videos)
  - flat-playlist JSON; do NOT filter on live_status (it is not populated
    in flat-playlist mode) — the /streams tab is reliably live broadcasts
    for this channel
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class LiveStream:
    url: str
    title: str


def _channel_streams_url(channel: str) -> str:
    """Normalize a handle/id/URL into the channel's /streams tab URL."""
    if channel.startswith("http://") or channel.startswith("https://"):
        return channel
    handle = channel if channel.startswith("@") else f"@{channel}"
    return f"https://www.youtube.com/{handle}/streams"


def fetch_live_streams(channel: str, limit: int = 5) -> list[LiveStream]:
    """Return up to `limit` most-recent streams from `channel` /streams tab.

    `channel` is a YT handle (@foo), id, or URL. Original (ru) titles are
    preserved via youtube:lang=ru. Returns newest-first.
    """
    url = _channel_streams_url(channel)
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--playlist-end", str(limit),
        "--extractor-args", "youtube:lang=ru",
        "-J",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:500] or "yt-dlp returned non-zero")

    data = json.loads(proc.stdout)
    entries = [e for e in (data.get("entries") or []) if e]
    out: list[LiveStream] = []
    for e in entries[:limit]:
        title = (e.get("title") or "").strip()
        vid = e.get("id") or e.get("url")
        if not vid:
            continue
        link = f"https://www.youtube.com/watch?v={vid}"
        out.append(LiveStream(url=link, title=title))
    return out
