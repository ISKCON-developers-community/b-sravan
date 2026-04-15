import asyncio
import mimetypes
import os
from pathlib import Path
from typing import Optional, Callable, Union
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeAudio
from telethon.errors import FloodWaitError, RPCError
from mutagen.mp3 import MP3
from mutagen.aac import AAC
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.flac import FLAC


class AudioUploadError(Exception):
    pass


class AudioFile:
    def __init__(
            self, 
            path: Union[str, Path], 
            artist: str = "", 
            title: str = ""
        ):
        self.path = Path(path).resolve()
        self.artist = artist
        self.title = title
        self._duration = None
        
        if not self.path.exists():
            raise AudioUploadError(f"File not found: {self.path}")
        if not self.path.is_file():
            raise AudioUploadError(f"Not a file: {self.path}")
    
    @property
    def duration(self) -> float:
        if self._duration is None:
            self._duration = self._get_duration()
        return self._duration
    
    def _get_duration(self) -> float:
        ext = self.path.suffix.lower()
        
        try:
            if ext == '.mp3':
                return MP3(str(self.path)).info.length
            elif ext == '.aac':
                return AAC(str(self.path)).info.length
            elif ext == '.ogg':
                try:
                    return OggOpus(str(self.path)).info.length
                except:
                    return OggVorbis(str(self.path)).info.length
            elif ext == '.flac':
                return FLAC(str(self.path)).info.length
            else:
                raise AudioUploadError(f"Unsupported format: {ext}")
        except Exception as e:
            raise AudioUploadError(f"Failed to read audio duration: {e}")
    
    @property
    def basename(self) -> str:
        return self.path.stem
    
    @property
    def name(self) -> str:
        return self.path.name


class CoverArt:
    def __init__(self, covers_dir: Union[str, Path] = "covers"):
        self.covers_dir = Path(covers_dir).resolve()
        self.default_cover = self.covers_dir / "cover.jpg"
    
    def get_path(self, artist: str) -> Optional[Path]:
        if not artist:
            artist = "unknown"
        
        safe_artist = "".join(c for c in artist if c.isalnum() or c in " _-")
        custom_cover = self.covers_dir / f"{safe_artist}.jpg"
        
        if custom_cover.is_file():
            return custom_cover
        if self.default_cover.is_file():
            return self.default_cover
        return None


class TelegramAudioUploader:
    def __init__(
        self,
        entity: str,
        api_id: int,
        api_hash: str,
        phone: str,
        default_artist: str = "",
        covers_dir: Union[str, Path] = "covers",
        session_name: Union[str, Path] = "uploader_session"
    ):
        self.entity = entity
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.default_artist = default_artist
        self.covers_dir = Path(covers_dir)
        self.session_name = str(Path(session_name).stem)
        self._client: Optional[TelegramClient] = None
        
        self._setup_mimetypes()
        self.cover_art = CoverArt(self.covers_dir)
        self._ensure_covers_dir()
    
    def _ensure_covers_dir(self):
        self.covers_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_mimetypes(self):
        mimetypes.add_type('audio/aac', '.aac')
        mimetypes.add_type('audio/ogg', '.ogg')
        mimetypes.add_type('audio/flac', '.flac')
    
    async def _get_client(self) -> TelegramClient:
        if self._client is None:
            session_path = Path(self.session_name)
            self._client = TelegramClient(
                str(session_path),
                self.api_id,
                self.api_hash
            )
            await self._client.start(phone=self.phone)
        return self._client
    
    async def _upload_file(
        self,
        audio: AudioFile,
        progress_callback: Optional[Callable] = None
    ):
        client = await self._get_client()
        
        artist = audio.artist or self.default_artist
        title = audio.title or audio.basename
        
        cover_path = self.cover_art.get_path(artist)
        
        try:
            await client.send_file(
                self.entity,
                str(audio.path),
                caption=f"{artist}={title}={audio.duration}",
                use_cache=False,
                part_size_kb=512,
                thumb=str(cover_path) if cover_path else None,
                attributes=[
                    DocumentAttributeAudio(
                        int(audio.duration),
                        title=title,
                        performer=artist
                    )
                ],
                progress_callback=progress_callback
            )
        except FloodWaitError as e:
            raise AudioUploadError(f"Flood wait: need to wait {e.seconds} seconds")
        except RPCError as e:
            raise AudioUploadError(f"RPC error: {e}")
        except Exception as e:
            raise AudioUploadError(f"Upload failed: {e}")
    
    async def upload(
        self,
        file_path: Union[str, Path],
        artist: str = "",
        title: str = "",
        progress_callback: Optional[Callable] = None
    ) -> bool:
        audio = AudioFile(file_path, artist, title)
        await self._upload_file(audio, progress_callback)
        return True
    
    async def upload_multiple(
        self,
        files: list[dict],
        progress_callback: Optional[Callable] = None
    ) -> dict:
        results = {
            "success": [],
            "failed": []
        }
        
        for file_info in files:
            try:
                await self.upload(
                    file_info["path"],
                    file_info.get("artist", ""),
                    file_info.get("title", ""),
                    progress_callback
                )
                results["success"].append(str(Path(file_info["path"])))
            except AudioUploadError as e:
                results["failed"].append({
                    "path": str(Path(file_info["path"])),
                    "error": str(e)
                })
        
        return results
    
    async def upload_directory(
        self,
        directory: Union[str, Path],
        pattern: str = "*.mp3",
        recursive: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> dict:
        directory = Path(directory).resolve()
        
        if not directory.is_dir():
            raise AudioUploadError(f"Not a directory: {directory}")
        
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        results = {
            "success": [],
            "failed": [],
            "total": len(files)
        }
        
        for file_path in files:
            try:
                await self.upload(str(file_path), progress_callback=progress_callback)
                results["success"].append(str(file_path))
            except AudioUploadError as e:
                results["failed"].append({
                    "path": str(file_path),
                    "error": str(e)
                })
        
        return results
    
    async def close(self):
        if self._client:
            await self._client.disconnect()
            self._client = None
    
    async def __aenter__(self):
        await self._get_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def sync_upload(
    entity: str,
    api_id: int,
    api_hash: str,
    phone: str,
    file_path: Union[str, Path],
    artist: str = "",
    title: str = "",
    default_artist: str = "",
    covers_dir: Union[str, Path] = "covers"
) -> bool:
    async def _upload():
        uploader = TelegramAudioUploader(
            entity=entity,
            api_id=api_id,
            api_hash=api_hash,
            phone=phone,
            default_artist=default_artist,
            covers_dir=covers_dir
        )
        try:
            return await uploader.upload(file_path, artist, title)
        finally:
            await uploader.close()
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(_upload())
    except RuntimeError:
        return asyncio.run(_upload())
