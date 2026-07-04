"""Pure caption builder — easy to unit-test, no I/O.

Output format (current first-release form, `with_date=False`):

    Artist #Artist_with_underscores
    Title
    CUSTOM_DESCRIPTION

Optional date suffix on the title line (toggle with `with_date=True`),
disabled by default for the first release:

    Artist #Artist_with_underscores
    Title - 04.07.26
    CUSTOM_DESCRIPTION
"""
from datetime import datetime


def hashtag(artist: str) -> str:
    """Spaces and dashes in the artist name become underscores for the hashtag."""
    return artist.replace(" ", "_").replace("-", "_")


def build_channel_caption(
    artist: str,
    title: str,
    description: str,
    with_date: bool = False,
    when: datetime | None = None,
) -> str:
    """Build the multi-line caption posted to the channel.

    - artist: speaker / devotee name (e.g. "Ванинатха Васу дас")
    - title: lecture title (e.g. "Б 10.13.14 Беспричинная милость")
    - description: custom line printed below (e.g. "Лекции @newjaipur")
    - with_date: when True, append " - DD.MM.YY" to the title line.
                 Disabled by default for the first release.
    - when: optional datetime for the date suffix; defaults to now.
            Ignored when with_date is False.

    `when` is injectable so tests can pin the date deterministically.
    """
    title_line = title
    if with_date:
        when = when or datetime.now()
        title_line = f"{title} - {when.strftime('%d.%m.%y')}"
    return (
        f"{artist} #{hashtag(artist)}\n"
        f"{title_line}\n"
        f"{description}\n"
    )
