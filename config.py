import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = os.getenv('CHANNEL_ID')
AGENT_ID = os.getenv('AGENT_ID') or ''
ENTITY = 'HK Minsk Audio bot'  # any session name
BOT_NAME = 'tmndsbvks'
PHONE = os.getenv('PHONE') or ''
API_HASH = os.getenv('API_HASH') or ''
API_ID = os.getenv('API_ID') or 0

YT_CHANNEL_ID = 'UCJAlTwrkQWgpIc5oRo-ryOw'
VIDEO_ITEMS_QUANTITY = 5

# mp3 config
GENRE = 'Кришна катха'
ALBUM_NAME = 'Лекции Минского храма Кришны'
DEFAULT_SPEAKER_NAME = 'Дас'
CUSTOM_DESCRIPTION = 'Лекции @newjaipur'

