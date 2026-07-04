"""Smoke tests for the tagger and the uploader's caption passthrough.

These don't touch the network — they exercise the local wiring so a refactor
that breaks the pipeline shows up before you push a 200 MB upload.
"""
import inspect
import shutil
from pathlib import Path

import pytest

from tagger import tag_mp3


# The uploader tests below only need `inspect.signature`, but they import the
# whole audio_uploader module which transitively imports telethon. If the test
# runner is using a python that doesn't have telethon installed (e.g. system
# python3 instead of the project venv), skip them cleanly with a clear message
# instead of failing with a confusing ModuleNotFoundError.
pytest.importorskip("telethon", reason="telethon required for uploader signature tests")


FIXTURE_MP3 = Path(__file__).resolve().parent / "_fixture.mp3"


@pytest.fixture
def mp3_copy(tmp_path):
    """Copy the project's test.mp3 into a tmp dir, return the path."""
    src = Path(__file__).resolve().parent.parent / "test.mp3"
    if not src.is_file():
        pytest.skip(f"test.mp3 not found at {src}")
    dest = tmp_path / "fixture.mp3"
    shutil.copy(src, dest)
    return dest


class TestTagger:
    def test_writes_basic_tags(self, mp3_copy):
        tag_mp3(mp3_copy, "Test Artist", "Test Title")
        from mutagen.id3 import ID3
        t = ID3(mp3_copy)
        assert t.get("TIT2") and "Test Title" in str(t.get("TIT2"))
        assert t.get("TPE1") and "Test Artist" in str(t.get("TPE1"))
        assert t.get("TALB") is not None
        assert t.get("TDRC") is not None
        assert t.get("TCON") is not None

    def test_falls_back_to_default_cover(self, mp3_copy):
        # The repo has covers/cover.jpg; the artist name has no matching file.
        tag_mp3(mp3_copy, "Unknown Speaker", "Whatever")
        from mutagen.id3 import ID3
        t = ID3(mp3_copy)
        # APIC frames are keyed by description; the default 'Cover' is used.
        apic_frames = t.getall("APIC")
        assert any(len(f.data) > 1000 for f in apic_frames), \
            "expected the default cover to be embedded"


class TestUploaderCaption:
    """The uploader must accept a `caption` kwarg and forward it to send_file."""

    def test_upload_signature_has_caption(self):
        from audio_uploader import TelegramAudioUploader
        params = list(inspect.signature(TelegramAudioUploader.upload).parameters)
        assert "caption" in params, f"upload() missing caption: {params}"

    def test_private_upload_file_has_caption(self):
        from audio_uploader import TelegramAudioUploader
        params = list(inspect.signature(
            TelegramAudioUploader._upload_file
        ).parameters)
        assert "caption" in params, f"_upload_file() missing caption: {params}"
