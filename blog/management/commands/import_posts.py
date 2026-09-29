"""Import Markdown files from posts/ into the DB. Idempotent by slug."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from blog.models import Category, Post

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
# Also support +++ TOML frontmatter from the old Zola posts
TOML_FM_RE = re.compile(r"^\+\+\+\n(.*?)\n\+\+\+\n?(.*)$", re.DOTALL)


def _parse_toml_simple(text: str) -> dict:
    """Tiny TOML subset for our post frontmatter — no toml lib required."""
    data: dict = {"extra": {}}
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            parsed: object = val[1:-1]
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            parsed = [
                p.strip().strip('"')
                for p in inner.split(",")
                if p.strip()
            ] if inner else []
        else:
            # date YYYY-MM-DD or bare word
            parsed = val.split("#", 1)[0].strip().strip('"')
        if section == "extra":
            data["extra"][key] = parsed
        else:
            data[key] = parsed
    return data


def parse_post_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = TOML_FM_RE.match(text) or FRONTMATTER_RE.match(text)
    if not m:
        raise CommandError(f"{path.name}: no frontmatter")
    meta = _parse_toml_simple(m.group(1))
    body = m.group(2).strip()
    extra = meta.get("extra") or {}
    title = meta.get("title")
    raw_date = meta.get("date")
    category = extra.get("category")
    summary = extra.get("summary")
    tags = extra.get("tags") or []
    if not title or not raw_date or not category or not summary:
        raise CommandError(
            f"{path.name}: need title, date, extra.category, extra.summary"
        )
    if isinstance(raw_date, str):
        published = date.fromisoformat(raw_date)
    else:
        raise CommandError(f"{path.name}: bad date")
    slug = path.stem
    return {
        "slug": slug,
        "title": title,
        "published_at": published,
        "category_slug": category,
        "summary": summary,
        "tags": tags if isinstance(tags, list) else [],
        "body": body,
    }


class Command(BaseCommand):
    help = "Import posts/*.md into Post rows (upsert by slug)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            type=Path,
            default=None,
            help="Posts directory (default: settings.POSTS_DIR)",
        )

    def handle(self, *args, **options):
        posts_dir: Path = options["dir"] or Path(settings.POSTS_DIR)
        if not posts_dir.is_dir():
            raise CommandError(f"No posts dir: {posts_dir}")
        files = sorted(posts_dir.glob("*.md"))
        if not files:
            self.stdout.write("No .md files to import.")
            return
        created = updated = 0
        for path in files:
            data = parse_post_file(path)
            cat, _ = Category.objects.get_or_create(
                slug=data["category_slug"],
                defaults={"name": data["category_slug"].title()},
            )
            obj, was_created = Post.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "published_at": data["published_at"],
                    "category": cat,
                    "summary": data["summary"],
                    "body": data["body"],
                    "tags": data["tags"],
                    "is_published": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
            self.stdout.write(f"{'created' if was_created else 'updated'}: {obj.slug}")
        self.stdout.write(self.style.SUCCESS(f"done: +{created} ~{updated}"))
