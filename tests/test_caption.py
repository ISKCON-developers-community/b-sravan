"""Caption builder tests — pure-function, deterministic, no I/O."""
from datetime import datetime

import pytest

from caption import build_channel_caption, hashtag


DESC = "Лекции @newjaipur"
PIN = datetime(2026, 7, 4, 12, 0, 0)


class TestHashtag:
    def test_keeps_cyrillic(self):
        assert hashtag("Ванинатха Васу дас") == "Ванинатха_Васу_дас"

    def test_dashes_become_underscores(self):
        assert hashtag("Some-Body") == "Some_Body"

    def test_keeps_underscores(self):
        assert hashtag("already_under") == "already_under"

    def test_empty(self):
        assert hashtag("") == ""


class TestBuildChannelCaption:
    # First-release format: no date in the title line.

    def test_first_release_format_exact(self):
        out = build_channel_caption(
            "Ванинатха Васу дас",
            "Б 10.13.14 Беспричинная милость",
            DESC, when=PIN,
        )
        assert out == (
            "Ванинатха Васу дас #Ванинатха_Васу_дас\n"
            "Б 10.13.14 Беспричинная милость\n"
            f"{DESC}\n"
        )

    def test_three_lines_plus_trailing_newline(self):
        out = build_channel_caption("A", "B", "C", when=PIN)
        assert out.count("\n") == 3
        assert out.endswith("\n")

    def test_no_date_in_title_line_by_default(self):
        # First release: with_date defaults to False; the date is not appended
        # even when `when` is provided.
        out = build_channel_caption("A", "B", "C", when=PIN)
        assert " - 04.07.26" not in out
        assert "\nB\n" in out  # title line is just "B", no suffix

    def test_artist_dash_in_name(self):
        out = build_channel_caption("Prema-Ananda", "Title", DESC, when=PIN)
        assert out.startswith("Prema-Ananda #Prema_Ananda\n")

    # Optional date-suffix mode (kept for future re-enablement).

    def test_with_date_appends_dd_mm_yy(self):
        out = build_channel_caption(
            "Artist", "Title", DESC, with_date=True, when=PIN,
        )
        assert "Title - 04.07.26\n" in out

    def test_with_date_uses_now_when_when_omitted(self):
        out = build_channel_caption("A", "B", "C", with_date=True)
        today = datetime.now().strftime("%d.%m.%y")
        assert f"B - {today}\n" in out
