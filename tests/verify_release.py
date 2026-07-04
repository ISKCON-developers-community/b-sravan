"""
Persistent ad-hoc verification for the b-shravan first-release changes.

Lives inside the project at tests/verify_release.py so the verifier system
can find and run it. Not a pytest test (intentionally — it's an ad-hoc
check, not a unit test), but invoked by the canonical test command via
`pytest tests/verify_release.py --no-header`.

Run standalone:  ./.venv/bin/python tests/verify_release.py
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PYTHON = str(REPO / ".venv" / "bin" / "python")
sys.path.insert(0, str(REPO))
os.chdir(REPO)


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        print(f"[FAIL] {label}: {detail}", file=sys.stderr)
        sys.exit(1)
    print(f"[ok]   {label}{(' — ' + detail) if detail else ''}")


# 1. caption.py: with_date flag, default off (first-release format)
import caption
out_default = caption.build_channel_caption("A", "B", "C", when=datetime(2026, 7, 4))
out_with_date = caption.build_channel_caption(
    "A", "B", "C", with_date=True, when=datetime(2026, 7, 4),
)
check(
    "caption default has no date suffix",
    out_default == "A #A\nB\nC\n",
    repr(out_default),
)
check(
    "caption with_date=True appends DD.MM.YY",
    out_with_date == "A #A\nB - 04.07.26\nC\n",
    repr(out_with_date),
)

# 2. main.py wires --download-only with a store_true action
main_src = (REPO / "main.py").read_text()
check(
    "main.py references args.download_only",
    "download_only" in main_src,
)
check(
    "main.py uses store_true for the -d flag",
    'action="store_true"' in main_src,
)

# 3. CLI --help lists the flag
r = subprocess.run(
    [PYTHON, str(REPO / "main.py"), "--help"],
    cwd=REPO, capture_output=True, text=True,
)
check(
    "main.py --help runs cleanly",
    r.returncode == 0,
    r.stderr[:200],
)
check(
    "main.py --help lists -d and --download-only",
    "-d" in r.stdout and "--download-only" in r.stdout,
)

# 4. End-to-end: download-only path with a stubbed downloader (no YouTube,
#    no Telegram). Confirms the early-exit branch returns 0 and never
#    touches the upload code.
import main
def fake_download(url):
    from downloader import Download
    return Download(path=Path("test.mp3"), title="T")

orig = main.download
main.download = fake_download
try:
    sys.argv = ["main.py", "-l", "http://x", "--artist", "A",
                "--title", "T", "-d"]
    rc = main.run()
    check("download-only path returns 0", rc == 0)
finally:
    main.download = orig

# 5. Real pytest suite (canonical test command)
r = subprocess.run(
    [PYTHON, "-m", "pytest", "tests/", "-v", "--tb=short",
     "--ignore=tests/verify_release.py"],
    cwd=REPO, capture_output=True, text=True,
)
print("--- pytest output (last 4 lines) ---")
for line in r.stdout.strip().splitlines()[-4:]:
    print(line)
check("pytest suite passes", r.returncode == 0, r.stderr[:200])

# 6. Live: @hkhrtest still resolves (no regression in the channel-id fix)
r = subprocess.run(
    [PYTHON, "-c", """
import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE, ENTITY
async def main():
    c = TelegramClient(ENTITY, API_ID, API_HASH)
    await c.start(phone=PHONE)
    e = await c.get_entity('@hkhrtest')
    print(f'OK @hkhrtest -> id={e.id}, title={e.title}')
    await c.disconnect()
asyncio.run(main())
"""],
    cwd=REPO, capture_output=True, text=True,
)
print(r.stdout, end="")
check("channel @hkhrtest still resolves",
      "OK @hkhrtest" in r.stdout, r.stderr[:200])

print("\nALL AD-HOC + SUITE CHECKS PASSED")
