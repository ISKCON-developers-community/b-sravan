"""End-to-end run() tests for the credential guard.

Verifies: -d / --download-only works without Telegram credentials in
.env, and the upload path without -d / creds falls back to download-only
(warns, rc=0). Each test spawns the tool in a subprocess from a temp
directory with a sanitized environment so config.py truly sees no
credentials (rather than relying on import-time caching or the
project's own .env).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent
PYTHON = str(REPO / ".venv" / "bin" / "python")


def _run_in_clean_env(args) -> subprocess.CompletedProcess:
    """Run main.py from a temp dir with no Telegram creds in the env.

    config.py calls load_dotenv() to read .env from CWD. By running from
    a temp dir that has no .env file, and by omitting the creds from the
    environment, we guarantee the guard sees empty values.
    """
    clean = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "LANG": os.environ.get("LANG", ""),
        # No API_ID, API_HASH, PHONE, CHANNEL_ID, ADMIN_ID — by omission.
    }
    with tempfile.TemporaryDirectory() as tmp:
        # Make sure the stub mp3 exists in the temp dir, since the tool
        # tries to tag it and would fail with FileNotFoundError otherwise.
        src_mp3 = REPO / "test.mp3"
        if src_mp3.is_file():
            (Path(tmp) / "test.mp3").write_bytes(src_mp3.read_bytes())
        # The tool is just an import of main.run() with sys.argv set.
        cmd = [PYTHON, "-c",
               f"import sys; sys.argv = {args!r}; "
               # Project root on sys.path so 'import main' finds it.
               f"sys.path.insert(0, '{REPO}'); "
               "import main; "
               "from pathlib import Path; "
               "from downloader import Download; "
               "main.download = lambda url: Download(path=Path('test.mp3'), title='T'); "
               "sys.exit(main.run())"]
        return subprocess.run(cmd, cwd=tmp, env=clean,
                              capture_output=True, text=True, timeout=15)


class TestRunGuards:
    def test_download_only_works_without_creds(self):
        r = _run_in_clean_env(
            ["main.py", "-l", "http://x", "--artist", "A", "--title", "T", "-d"]
        )
        # Some log lines from main may print; just check the exit code and
        # that the credential guard did NOT abort.
        assert r.returncode == 0, (
            f"download-only should succeed without creds; "
            f"got rc={r.returncode}\nstdout: {r.stdout}\nstderr: {r.stderr}"
        )
        assert "must be set in .env" not in r.stdout + r.stderr, (
            f"credential guard should not fire in -d mode; "
            f"got: {r.stdout + r.stderr}"
        )
        assert "download-only mode" in r.stdout + r.stderr

    def test_upload_path_requires_creds(self):
        r = _run_in_clean_env(
            ["main.py", "-l", "http://x", "--artist", "A", "--title", "T"]
        )
        # Without creds and without -d, run() falls back to download-only
        # (rc=0) and warns, rather than hard-failing with rc=2.
        assert r.returncode == 0, (
            f"missing creds should fall back to download-only (rc=0); "
            f"got rc={r.returncode}\nstdout: {r.stdout}\nstderr: {r.stderr}"
        )
        assert "falling back to download-only" in r.stdout + r.stderr, (
            f"expected the fallback warning; got: {r.stdout + r.stderr}"
        )
        assert "download-only mode" in r.stdout + r.stderr
