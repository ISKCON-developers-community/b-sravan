# b-shravan

YouTube → Telegram channel MP3 poster. Pick a video (URL on the CLI or
interactively), tag the audio with ID3 metadata, and post it to a
Telegram channel with a formatted caption.

## Features

- **CLI** (`-l URL` / `--link URL`) or **interactive TUI** — pick a
  video, type the artist and title, done.
- **Auto-tagging** with `mutagen` — artist, title, album, year, genre,
  cover art (`covers/{artist}.jpg` or fallback `covers/cover.jpg`).
- **Formatted caption** posted to the channel (see [Caption format](#caption-format)).
- **`-d` / `--download-only`** — download and tag, skip the upload.
  Useful for batch review or scripted re-uploads.
- **`-c` / `--channel`** — override the destination channel for a
  single run without editing `.env`.
- **`--artist` / `--title`** — skip the interactive prompts for
  scripted use.

## Requirements

- Python 3.13 or newer
- A Telegram account + an API id/hash from
  [my.telegram.org/apps](https://my.telegram.org/apps) (optional, use -d flag to scip uploading to telegra)
- A Telegram channel you can post to (you must be a member and
  an admin; the bot or your user account is used to post)
- `ffmpeg` and `ffprobe` on `PATH` — `yt-dlp` needs them to extract
  audio. Install via your package manager:
  - Debian/Ubuntu: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: download from [ffmpeg.org](https://ffmpeg.org/download.html)
    and add the `bin` folder to `PATH`

## Install (Unix / Linux / macOS)

```sh
git clone https://github.com/ISKCON-developers-community/b-sravan.git

cd b-shravan

# Create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install runtime dependencies
pip install -r requirements.txt

# (Optional, for running tests)
pip install pytest

# Copy the env template and fill in your credentials
cp .env.example .env
$EDITOR .env
```

You need (only for uploading) four values in `.env`:

| Variable     | Where to get it                                          |
|--------------|----------------------------------------------------------|
| `API_ID`     | `my.telegram.org/apps` → "App api_id"                    |
| `API_HASH`   | `my.telegram.org/apps` → "App api_hash"                  |
| `PHONE`      | Your phone number in international format (`+375…`)      |
| `CHANNEL_ID` | `@channel_username` (recommended), or numeric id, or invite link |

On the **first run** telethon will ask for a login code sent to your
Telegram app — this is the normal authorization flow. The session is
saved to `<session_name>.session` in the project root, so the
next runs are silent.

## Install (Windows)

If you don't have Python yet:

1. Download the latest Python 3.13+ installer from
   [python.org/downloads/windows](https://www.python.org/downloads/windows/).
2. Run the installer. **Important:** on the first screen, tick
   **"Add python.exe to PATH"** before clicking "Install Now".
3. Verify in a fresh `cmd.exe` or PowerShell window:
   ```powershell
   python --version
   ```
   You should see `Python 3.13.x` (or newer).

Then in `cmd.exe` or PowerShell:

```powershell
git clone <your-fork-or-this-repo-url> b-shravan
cd b-shravan

python -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt

# (Optional, for running tests)
pip install pytest

copy .env.example .env
notepad .env
```

Fill in the same four values as on Unix (`API_ID`, `API_HASH`,
`PHONE`, `CHANNEL_ID` — see the table above).

On the **first run** telethon will ask for a login code in the
terminal; enter the code Telegram sends to your app. The session is
saved to `HK Minsk Audio bot.session` so subsequent runs are silent.

> Tip: the `python` command on Windows sometimes opens the Microsoft
> Store stub instead of your real install. If that happens, run
> `python3` instead, or use the full path to the venv python:
> `.\.venv\Scripts\python.exe main.py …`

## Usage

Interactive TUI (prompts for the URL, then artist, then title):

```sh
python main.py
```

One-shot, every flag on the command line:

```sh
python main.py -l "https://youtu.be/VIDEO_ID" \
    --artist "Ванинатха Васу дас" \
    --title "Б 10.13.14 Беспричинная милость"
```

Override the channel for a single run:

```sh
python main.py -l "https://youtu.be/VIDEO_ID" \
    --artist "..." --title "..." -c "@otherchannel"
```

Download and tag only, skip the upload (the file is left in
`./downloads/` for manual review):

```sh
python main.py -l "https://youtu.be/VIDEO_ID" \
    --artist "..." --title "..." -d
```

## Caption format

The post sent to the channel has the form (first release; date is
excluded by default):

```
Artist #Artist_with_underscores
Title
Лекции @newjaipur
```

The description line is read from `CUSTOM_DESCRIPTION` in `config.py`.
Spaces and dashes in the artist name are converted to underscores in
the hashtag (e.g. `Prema-Ananda` → `#Prema_Ananda`).

The date suffix (`- DD.MM.YY` on the title line) is available behind
`with_date=True` in `caption.py` — flip the default when you're ready
to re-enable it. The unit tests cover both modes.

## Tests

```sh
python -m pytest tests/
```

Two test files (`tests/test_caption.py`, `tests/test_pipeline.py`)
cover the caption builder, the ID3 tagger, and the uploader
signature. A `tests/verify_release.py` ad-hoc script runs the full
suite plus a live channel-resolution smoke test:

```sh
python tests/verify_release.py
```

## Project layout

```
main.py                CLI entry: -l URL + --artist/--title/-d/-c
downloader.py          yt-dlp wrapper → mp3 in ./downloads/
tagger.py              mutagen ID3 writer (artist, title, album, year, genre, cover)
caption.py             pure caption builder (testable, no I/O)
audio_uploader.py      TelegramAudioUploader class (Telethon, audio metadata)
config.py              .env loader and project constants
tests/                 pytest suite + ad-hoc verify_release.py
covers/                per-artist covers; falls back to cover.jpg (gitignored)
downloads/             yt-dlp output lands here (gitignored)
.env                   your credentials (gitignored, copy from .env.example)
HK Minsk Audio bot.session  telethon auth (gitignored, created on first run)
```

## Notes

- Downloaded mp3s are kept in `./downloads/` (gitignored) so you can
  re-upload if a tag was wrong. Delete them manually when you want.
- The Telethon session (`HK Minsk Audio bot.session`) is the
  authorization token for your account. **Back it up** — without it
  you'll need to re-authorize (re-enter the SMS code) on the next
  install.
- `CHANNEL_ID` accepts a numeric chat id, a public `@username`, or
  an invite link. **Recommended: use the `@username` form** (e.g.
  `@hkhrtest`) — it's human-readable, survives id migrations, and
  dodges a telethon edge case where the public id (the digits in
  `t.me/foo` links) and the canonical id (the `-100…` form telethon
  stores internally) can mismatch on a fresh session. To find a
  username, look at the channel's `t.me/<username>` link; to find
  the canonical id, forward any post from the channel to
  `@RawDataBot` or `@userinfobot`.
- For the `-d` / `--download-only` mode, the file is left in
  `./downloads/` for you to inspect, re-tag, or upload later. The
  current run does **not** re-upload it.
- **The four Telegram credentials in `.env` are only required for
  uploading.** With `-d` / `--download-only` you can run the tool
  with no `.env` at all (or with a partial one) — it will download
  and tag the mp3, then exit without contacting Telegram. The
  full pipeline (no `-d`) still requires `API_ID`, `API_HASH`,
  `PHONE`, and `CHANNEL_ID` to be set.
