"""Project config — loads .env via python-dotenv, exposes typed constants.

Top section: tunable defaults (edit freely, NOT secrets)
Bottom section: immutable credentials (loaded from .env, never edit)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project root — the directory containing this config.py. All relative
# paths below are resolved against this so the script works from any CWD.
BASE_DIR = Path(__file__).resolve().parent


# ──────────────────────────────────────────────────────────────────────
# TUNABLE DEFAULTS — edit in this file, not in .env
# ──────────────────────────────────────────────────────────────────────


# Audio quality for yt-dlp mp3 extraction (kbps)
AUDIO_BITRATE = 128

# ID3 tags applied to every uploaded mp3
#TODO default album name - "Лекции Минского храма Кришны (Новый Джайпур)"  Add as parameter ni CLI
ALBUM_NAME = "Лекции Минского храма Кришны"   # placeholder: your YT channel name
#TODO change default genre - katha. Add as parameter in CLI
GENRE = "Podcast"                             # ID3 genre tag
CUSTOM_DESCRIPTION = "Лекции @newjaipur"       # bottom line of channel caption
DEFAULT_SPEAKER_NAME = "Дас"                  # fallback when no artist supplied

# Filesystem — resolved against BASE_DIR so the script works from any CWD
DOWNLOADS_DIR = (BASE_DIR / "downloads").resolve()   # where yt-dlp lands mp3 files
COVERS_DIR = (BASE_DIR / "covers").resolve()         # per-artist / default cover art

# Telethon session filename (without .session suffix)
ENTITY = "b-shravan-session"

# Channel destination for uploads. CLI --channel overrides this.
# Accepts: @username, -100... canonical id, public id, or invite link
CHANNEL_ID = "@hkhrtest" #TODO consider move in .env because I have prod and dev environment

# YouTube source channel for the live-stream picker (no API key; yt-dlp).
# Handle (@foo), id, or URL. Picker lists the 5 newest past live streams.
YT_CHANNEL = "@SoznanieKrishnyBLR"
YT_PICKER_LIMIT = 5

# Personal Telegram user id (for future "send copy to me" feature)
ADMIN_ID = 0


# ──────────────────────────────────────────────────────────────────────
# IMMUTABLE CREDENTIALS — loaded from .env, DO NOT EDIT
# ──────────────────────────────────────────────────────────────────────

# Telegram API credentials (from my.telegram.org/apps)
API_ID = int(os.getenv("API_ID") or 0)
API_HASH = os.getenv("API_HASH") or ""
PHONE = os.getenv("PHONE") or ""
