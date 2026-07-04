"""ID3 tagger — writes artist, title, album, year, genre, cover into an mp3."""
from datetime import date
from pathlib import Path
from typing import Union

from mutagen.id3 import ID3, ID3NoHeaderError, TDRC, TIT2, TALB, TPE1, TCON, APIC

from config import ALBUM_NAME, GENRE


def _cover_path(artist: str) -> Path | None:
    """Look for covers/{artist}.jpg, then covers/cover.jpg. Return None if neither."""
    covers = Path("covers")
    custom = covers / f"{artist}.jpg"
    if custom.is_file():
        return custom
    default = covers / "cover.jpg"
    if default.is_file():
        return default
    return None


def tag_mp3(file_path: Union[str, Path], artist: str, title: str) -> None:
    """Write ID3v2 tags onto an mp3 in place.

    - TPE1 (artist), TIT2 (title), TALB (album from config), TDRC (year today),
      TCON (genre from config), APIC (cover art if available).
    - If the file has no ID3 header yet, one is created.
    """
    file_path = Path(file_path)
    try:
        id3 = ID3(file_path)
    except ID3NoHeaderError:
        id3 = ID3()  # fresh tag set; .save() will create the header

    id3.delall("TPE1")
    id3.delall("TIT2")
    id3.delall("TALB")
    id3.delall("TDRC")
    id3.delall("TCON")
    id3.delall("APIC")

    id3.add(TIT2(encoding=3, text=title))
    id3.add(TALB(encoding=3, text=ALBUM_NAME))
    id3.add(TPE1(encoding=3, text=artist))
    id3.add(TDRC(encoding=3, text=str(date.today().year)))
    id3.add(TCON(encoding=3, text=GENRE))

    cover = _cover_path(artist)
    if cover is not None:
        id3.add(APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,            # cover (front)
            desc="Cover",
            data=cover.read_bytes(),
        ))

    id3.save(file_path)
