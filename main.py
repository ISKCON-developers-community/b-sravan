#!/usr/bin/env -S ./.venv/bin/python
"""b-shravan — pick a YouTube video, tag the audio, post it to a Telegram channel.

Two modes:
  - With -l URL:   one-shot, URL passed on the command line.
  - Without -l:    interactive TUI — prompts for the URL.

The Telegram channel is read from CHANNEL_ID in .env, overridable with --channel.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

from audio_uploader import TelegramAudioUploader, AudioUploadError
from caption import build_channel_caption
from config import (
    API_HASH, API_ID, BASE_DIR, CHANNEL_ID, COVERS_DIR, CUSTOM_DESCRIPTION, ENTITY, PHONE,
)
from downloader import download
from tagger import tag_mp3

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("b-shravan")


# ---------- CLI plumbing ----------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Download a YouTube video, tag the audio, post it to a Telegram channel.",
    )
    p.add_argument(
        "-l", "--link", default=None,
        help="YouTube URL. If omitted, you will be prompted interactively.",
    )
    p.add_argument(
        "-c", "--channel", default=None,
        help="Override CHANNEL_ID from .env (chat id, @username, or invite link).",
    )
    p.add_argument(
        "--artist", default=None,
        help="Skip the artist prompt (useful for scripting).",
    )
    p.add_argument(
        "--title", default=None,
        help="Skip the title prompt (useful for scripting).",
    )
    p.add_argument(
        "-d", "--download-only", action="store_true",
        help="Download and tag the mp3, but skip the Telegram upload. "
             "The file is left in DOWNLOADS_DIR for manual review or later upload.",
    )
    return p.parse_args()


def prompt_url() -> str:
    while True:
        url = input("YouTube URL: ").strip()
        if url:
            return url
        print("URL cannot be empty.")


def prompt_tag(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        if raw:
            return raw
        print("Cannot be empty.")


def prompt_artist_title() -> tuple[str, str]:
    while True:
        raw = input("Tags as 'Artist|Title': ").strip()
        if "|" in raw:
            artist, _, title = raw.partition("|")
            artist, title = artist.strip(), title.strip()
            if artist and title:
                return artist, title
        print("Format must be 'Artist|Title' (both parts non-empty).")


# ---------- Progress --------------------------------------------------------

def _progress(received: int, total: int) -> None:
    if total:
        pct = received / total * 100
        sys.stdout.write(
            f"\r  -> uploading: {received/1024/1024:6.1f} / "
            f"{total/1024/1024:6.1f} MB ({pct:5.1f}%)"
        )
        sys.stdout.flush()


# ---------- Upload (single event loop) -------------------------------------

async def _post_to_channel(
    channel: str, mp3_path: Path, artist: str, title: str, caption: str,
) -> None:
    """Owns the uploader's client lifecycle on one event loop.

    Telethon sessions are bound to the loop where start() was called, so
    both upload() and close() must run on the same loop.
    """
    uploader = TelegramAudioUploader(
        entity=channel,
        api_id=API_ID,
        api_hash=API_HASH,
        phone=PHONE,
        default_artist=artist,
        covers_dir=COVERS_DIR,
        session_name=Path(BASE_DIR / f"{ENTITY}.session"),
    )
    try:
        await uploader.upload(
            mp3_path, artist=artist, title=title,
            caption=caption, progress_callback=_progress,
        )
    finally:
        sys.stdout.write("\n")
        await uploader.close()


# ---------- Main flow -------------------------------------------------------

def run() -> int:
    #TODO create ASCII art banner
    args = parse_args()

    if not API_ID or not API_HASH or not PHONE:
        if args.download_only:
            log.info("API_ID / API_HASH / PHONE not set in .env; "
                     "download-only mode does not require them")
        else:
            print("API_ID / API_HASH / PHONE must be set in .env", file=sys.stderr)
            return 2
    channel = args.channel or CHANNEL_ID
    if not channel and not args.download_only:
        print(
            "No channel target. Set CHANNEL_ID in .env or pass --channel.",
            file=sys.stderr,
        )
        return 2

    url = args.link or prompt_url()

    # 1. Download
    log.info("downloading %s", url)
    try:
        dl = download(url)
    except Exception as e:
        log.error("download failed: %s", e)
        return 1
    log.info("downloaded -> %s (title=%r)", dl.path, dl.title)

    # 2. Prompt for tags (with sensible defaults for scripting)
    if args.artist and args.title:
        artist, title = args.artist, args.title
    else:
        default_artist = args.artist or ""
        default_title = args.title or dl.title
        artist = prompt_tag("Artist", default_artist) if not args.artist else args.artist
        title = prompt_tag("Title",  default_title)  if not args.title  else args.title
    log.info("tags: artist=%r title=%r", artist, title)

    # 3. Tag the mp3
    tag_mp3(dl.path, artist, title)
    log.info("id3 tags written")

    # 4. Build caption
    caption = build_channel_caption(artist, title, CUSTOM_DESCRIPTION)
    print("----caption----")
    print(caption, end="")
    print("----------------")

    if args.download_only:
        log.info("download-only mode: skipping upload")
        print(f"File saved at: {dl.path}")
        return 0

    # 5. Upload
    log.info("posting to %s", channel)
    t0 = time.monotonic()
    try:
        asyncio.run(_post_to_channel(channel, dl.path, artist, title, caption))
    except AudioUploadError as e:
        log.error("upload failed: %s", e)
        return 1
    log.info("done in %.1fs", time.monotonic() - t0) #TODO what is done. Provide more info. Published into <channel>
    return 0

if __name__ == "__main__":
    sys.exit(run())
