"""Commit history for the homepage.

Reads `git log` when the checkout is present. The Docker image has no `.git`,
so the build writes `blog/data/repo_history.json` and the page reads that.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_WEB = "https://github.com/drresist/drresist.ru"
HISTORY_LIMIT = 50
MOSCOW = ZoneInfo("Europe/Moscow")
_CACHE: dict[str, dict] = {}


def history_from_git(repo: Path, limit: int = HISTORY_LIMIT) -> dict:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "log",
            f"-n{limit}",
            "--pretty=format:%H%x1f%cI%x1f%s",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    commits = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        sha, committed_at, subject = line.split("\x1f", 2)
        when = datetime.fromisoformat(committed_at).astimezone(MOSCOW)
        commits.append(
            {
                "sha": sha,
                "short": sha[:7],
                "date": when.date().isoformat(),
                "committed_at": when.isoformat(),
                "subject": subject,
                "url": f"{REPO_WEB}/commit/{sha}",
            }
        )
    return {"commits": commits}


def load_history(repo: Path) -> dict:
    key = _cache_key(repo)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    history = _read(repo)
    _CACHE.clear()
    _CACHE[key] = history
    return history


def _read(repo: Path) -> dict:
    if (repo / ".git").exists():
        try:
            return history_from_git(repo)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
    path = repo / "blog" / "data" / "repo_history.json"
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        commits = data.get("commits") or []
        return {"commits": commits}
    return {"commits": []}


def _cache_key(repo: Path) -> str:
    head = repo / ".git" / "HEAD"
    if not head.is_file():
        snapshot = repo / "blog" / "data" / "repo_history.json"
        if snapshot.is_file():
            return f"file:{snapshot.stat().st_mtime_ns}"
        return "empty"
    text = head.read_text(encoding="utf-8").strip()
    if text.startswith("ref:"):
        ref = repo / ".git" / text.split(" ", 1)[1]
        if ref.is_file():
            return ref.read_text(encoding="utf-8").strip()
    return text
