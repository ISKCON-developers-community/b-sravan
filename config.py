"""Project config — loads .env via python-dotenv, exposes typed constants."""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials (from my.telegram.org/apps)
API_ID = int(os.getenv("API_ID") or 0)
API_HASH = os.getenv("API_HASH") or ""
PHONE = os.getenv("PHONE") or ""

# Telethon session file label (any name; .session is appended automatically)
ENTITY = "HK Minsk Audio bot"

# Channel destination for uploads. CLI --channel overrides this.
# Accepts any of:
#   @channel_username     — recommended; works regardless of id format quirks
#   -1001234567890        — canonical id for supergroups/channels
#   1402888933            — public id (works but has rare resolution edge cases)
#   https://t.me/foo      — invite link
CHANNEL_ID = os.getenv("CHANNEL_ID") or ""

# Optional: personal Telegram user id (currently unused in the upload flow;
# reserved for any future "send a copy to me" feature).
ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)

# ID3 / channel caption defaults
ALBUM_NAME = "Лекции Минского храма Кришны"
GENRE = "Кришна катха"
CUSTOM_DESCRIPTION = "Лекции @newjaipur"
DEFAULT_SPEAKER_NAME = "Дас"

# Where downloaded mp3s land (created on first run, gitignored).
DOWNLOADS_DIR = "downloads"
