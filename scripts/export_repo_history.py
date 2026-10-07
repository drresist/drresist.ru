#!/usr/bin/env python3
"""Print commit history JSON for the Docker image. Usage: export_repo_history.py [repo]."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from blog.repo_history import history_from_git  # noqa: E402

repo = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
json.dump(history_from_git(repo), sys.stdout, ensure_ascii=False)
sys.stdout.write("\n")
