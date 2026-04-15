from config import ENTITY, API_ID, API_HASH, PHONE, BOT_NAME, DEFAULT_SPEAKER_NAME
from audio_uploader import TelegramAudioUploader
from pathlib import Path
import asyncio

async def main():
    uploader = TelegramAudioUploader(
        entity=BOT_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        phone=PHONE,
        default_artist=DEFAULT_SPEAKER_NAME,
        covers_dir=Path("."),
        session_name=Path(ENTITY)
    )
    
    async with uploader:
        await uploader.upload(Path("test.mp3"))
"""
        results = await uploader.upload_directory(
            Path("music/"),
            pattern="*.mp3",
            recursive=True
        )
        print(f"Uploaded: {len(results['success'])}/{results['total']}")
"""
asyncio.run(main())
