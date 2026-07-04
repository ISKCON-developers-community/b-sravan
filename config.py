"""Project config — loads .env via python-dotenv, exposes typed constants.

Top section: tunable defaults (edit freely, NOT secrets)
Bottom section: immutable credentials (loaded from .env, never edit)
"""
import os
from dotenv import load_dotenv

load_dotenv()


# ──────────────────────────────────────────────────────────────────────
# TUNABLE DEFAULTS — edit in this file, not in .env
# ──────────────────────────────────────────────────────────────────────

# Audio quality for yt-dlp mp3 extraction (kbps)
AUDIO_BITRATE = 128

# ID3 tags applied to every uploaded mp3
ALBUM_NAME = "Лекции Минского храма Кришны"   # placeholder: your YT channel name
GENRE = "Podcast"                             # ID3 genre tag
CUSTOM_DESCRIPTION = "Лекции @newjaipur"       # bottom line of channel caption
DEFAULT_SPEAKER_NAME = "Дас"                  # fallback when no artist supplied

# Filesystem
DOWNLOADS_DIR = "downloads"                    # where yt-dlp lands mp3 files

# Telethon session filename (without .session suffix)
ENTITY = "b-shravan-session"

# Channel destination for uploads. CLI --channel overrides this.
# Accepts: @username, -100... canonical id, public id, or invite link
CHANNEL_ID = "@hkhrtest"

# Personal Telegram user id (for future "send copy to me" feature)
ADMIN_ID = 0


# ──────────────────────────────────────────────────────────────────────
# IMMUTABLE CREDENTIALS — loaded from .env, DO NOT EDIT
# ──────────────────────────────────────────────────────────────────────

# Telegram API credentials (from my.telegram.org/apps)
API_ID = int(os.getenv("API_ID") or 0)
API_HASH = os.getenv("API_HASH") or ""
PHONE = os.getenv("PHONE") or ""
