# Changelog

All notable changes to b-shravan are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-07-19

### Added
- **YouTube live-stream picker** (`yt_picker.py`): when run without `-l`
  and Telegram creds are present, the tool fetches the 5 most recent past
  live streams from `config.YT_CHANNEL` (default `@SoznanieKrishnyBLR`)
  via yt-dlp and shows a numbered menu — no more copy-pasting URLs. Falls
  back to a manual prompt on any fetch failure. Original Russian titles are
  preserved (`--extractor-args youtube:lang=ru`).
- **Credential fallback**: if `API_ID` / `API_HASH` / `PHONE` are missing
  and `-d` is not passed, `main.py` now warns and switches to
  download-only mode instead of hard-failing with exit code 2.
- **Clean Ctrl+C**: the entry point catches `KeyboardInterrupt` and exits
  with code 130 plus a one-line message instead of a raw traceback.

### Changed
- **Config layout reorganised**: `config.py` now has two clearly delimited
  sections — `TUNABLE DEFAULTS` (top, edit freely: `AUDIO_BITRATE`,
  `ALBUM_NAME`, `GENRE`, `CUSTOM_DESCRIPTION`, `DEFAULT_SPEAKER_NAME`,
  `DOWNLOADS_DIR`, `ENTITY`, `CHANNEL_ID`, `ADMIN_ID`, `YT_CHANNEL`,
  `YT_PICKER_LIMIT`) and `IMMUTABLE CREDENTIALS` (bottom, loaded from
  `.env`: `API_ID`, `API_HASH`, `PHONE`).
- **`.env` now needs only three secrets** (`API_ID`, `API_HASH`,
  `PHONE`). The channel id, session name, ID3 tags, download dir, audio
  bitrate, and YouTube source channel are all configured in `config.py`.
- **Session filename uses `ENTITY` config** instead of a hardcoded
  string: `b-shravan-session.session` by default.
- **Audio bitrate is configurable** via `config.AUDIO_BITRATE`
  (default 128 kbps, was hardcoded 192).
- **All paths are now absolute** (anchored to `BASE_DIR = project root`),
  so the tool works correctly when launched from any working directory.
  Previously relative `covers/`, `downloads/`, and the Telethon session
  were created in the CWD.
- **Video title is fetched before downloading**: `run()` now does a cheap
  metadata-only yt-dlp pass to prefill the Artist/Title prompts, so the
  user confirms the title *before* the (often 90-minute) audio download
  starts.
- **All TODO/FIXME comments removed** from project source.
- README updated to reflect the 3-secret `.env` + tunable `config.py`
  split and the new YouTube picker, on both Unix and Windows install paths.

### Notes
- No breaking changes for existing users. If your `.env` had
  `CHANNEL_ID` or `ADMIN_ID`, move those values into `config.py`
  and remove them from `.env`.
- The Telethon session file is now `b-shravan-session.session` for
  fresh installs. Existing `HK Minsk Audio bot.session` files still
  work (rename or back up as preferred).

## [0.1.0] - 2026-07-04

First public release. YouTube → Telegram channel poster with a
configurable caption and a download-only mode.

### Added
- CLI entry point (`main.py`) with `-l` / `--link` for one-shot YouTube
  URLs and a fallback interactive TUI prompt.
- `-c` / `--channel` flag to override the destination chat per run
  (accepts numeric id, `@username`, or invite link).
- `--artist` and `--title` flags to skip the interactive prompts for
  scripted use.
- `-d` / `--download-only` flag — downloads and tags the mp3, leaves it
  in `./downloads/`, skips the Telegram upload entirely. Works without
  any `.env` credentials.
- yt-dlp wrapper (`downloader.py`) producing 128k mp3 in `./downloads/`.
- mutagen-based ID3 tagger (`tagger.py`) writing artist, title, album
  (from `config.ALBUM_NAME`), year, genre (from `config.GENRE`), and
  embedded cover art (per-artist or fallback to `covers/cover.jpg`).
- Pure caption builder (`caption.py`) producing the channel post text.
  First-release format has no date; an optional `with_date=True` flag
  appends the `DD.MM.YY` suffix for future re-enablement.
- Telegram audio uploader class (`audio_uploader.py`) accepts a custom
  caption and reports live upload progress.
- `python-dotenv`-based config (`config.py`) with a `.env.example`
  template and `.gitignore` rules that keep `.env`, the Telethon
  session, the venv, and downloaded mp3s out of the repo.
- 16 pytest cases (caption + tagger + uploader signature + run guards)
  and a persistent `tests/verify_release.py` ad-hoc check that
  re-validates the full release.
- README with Unix (`python3 -m venv`) and Windows install
  instructions, ffmpeg dependency note, and channel-id gotcha.

### Notes for first-time users
- The Telethon session (`HK Minsk Audio bot.session` by default) is
  created on first run. Back it up — without it you'll need to
  re-authorize.
- Recommended: set `CHANNEL_ID=@channel_username` in `.env` rather
  than a numeric id; it dodges a known telethon edge case where the
  public id and the canonical id mismatch on a fresh session.
- For batch-downloading + tagging a YouTube playlist without
  ever contacting Telegram, use `-d` (works without `.env` at all).
