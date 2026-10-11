"""Project config — loads .env via python-dotenv, exposes typed constants.

Three-tier priority (highest → lowest):
  1. CLI flags          (one-off override)
  2. .env file          (user's local config, gitignored)
  3. config.py defaults (committed, ships with repo)

Edit the tunables below for committed defaults. To override locally
without editing this file, set the same key in your .env (gitignored).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _env_str(key: str, default: str) -> str:
    """Read a string from .env, fall back to the committed default.

    Empty strings in .env are treated as "not set" so users can
    comment/uncomment lines freely.
    """
    val = os.getenv(key)
    return val if val else default


def _env_int(key: str, default: int) -> int:
    """Read an int from .env, fall back to the committed default."""
    val = os.getenv(key)
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default


# Project root — the directory containing this config.py. All relative
# paths below are resolved against this so the script works from any CWD.
BASE_DIR = Path(__file__).resolve().parent


# ──────────────────────────────────────────────────────────────────────
# TUNABLE DEFAULTS — edit here to change shipped defaults.
# Override any of these locally by setting the same key in .env
# (gitignored). The lookup helpers are _env_str() / _env_int() above.
# ──────────────────────────────────────────────────────────────────────


# Audio quality for yt-dlp mp3 extraction (kbps)
AUDIO_BITRATE = _env_int("AUDIO_BITRATE", 128)

# ID3 tags applied to every uploaded mp3
#TODO default album name - "Лекции Минского храма Кришны (Новый Джайпур)"  Add as parameter ni CLI
ALBUM_NAME = _env_str("ALBUM_NAME", "Лекции Минского храма Кришны")
#TODO change default genre - katha. Add as parameter in CLI
GENRE = _env_str("GENRE", "Podcast")                             # ID3 genre tag
CUSTOM_DESCRIPTION = _env_str("CUSTOM_DESCRIPTION", "Лекции @newjaipur")
DEFAULT_SPEAKER_NAME = _env_str("DEFAULT_SPEAKER_NAME", "Дас")  # fallback when no artist supplied

# Filesystem — resolved against BASE_DIR so the script works from any CWD.
# Override in .env only if you really need a custom layout.
DOWNLOADS_DIR = (BASE_DIR / _env_str("DOWNLOADS_DIR", "downloads")).resolve()
COVERS_DIR = (BASE_DIR / _env_str("COVERS_DIR", "covers")).resolve()

# Telethon session filename (without .session suffix)
ENTITY = _env_str("ENTITY", "b-shravan-session")

# Channel destination for uploads. CLI --channel overrides this.
# Accepts: @username, -100... canonical id, public id, or invite link
# Override in .env to switch between dev/prod without editing this file.
CHANNEL_ID = _env_str("CHANNEL_ID", "@hkhrtest")

# YouTube source channel for the live-stream picker (no API key; yt-dlp).
# Handle (@foo), id, or URL. Picker lists the 5 newest past live streams.
YT_CHANNEL = _env_str("YT_CHANNEL", "@SoznanieKrishnyBLR")
YT_PICKER_LIMIT = _env_int("YT_PICKER_LIMIT", 5)

# Personal Telegram user id (for future "send copy to me" feature)
ADMIN_ID = _env_int("ADMIN_ID", 0)


# ──────────────────────────────────────────────────────────────────────
# IMMUTABLE CREDENTIALS — loaded from .env, DO NOT EDIT
# ──────────────────────────────────────────────────────────────────────


# Telegram API credentials (from my.telegram.org/apps)
API_ID = int(os.getenv("API_ID") or 0)
API_HASH = os.getenv("API_HASH") or ""
PHONE = os.getenv("PHONE") or ""