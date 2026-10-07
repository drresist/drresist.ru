"""Import Markdown files from posts/ into the DB. Idempotent by slug."""

from __future__ import annotations

import tomllib
from datetime import date, datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from blog.models import CATEGORIES, Post

CATEGORY_SLUGS = {slug for slug, _name in CATEGORIES}


def parse_post_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("+++\n"):
        raise CommandError(f"{path.name}: expected TOML frontmatter (+++)")
    end = text.find("\n+++\n", 4)
    if end == -1:
        raise CommandError(f"{path.name}: frontmatter is not closed")
    try:
        meta = tomllib.loads(text[4:end])
    except tomllib.TOMLDecodeError as exc:
        raise CommandError(f"{path.name}: {exc}") from exc

    extra = meta.get("extra") or {}
    title = meta.get("title")
    raw_date = meta.get("date")
    category = extra.get("category")
    summary = extra.get("summary")
    if not title or not raw_date or not category or not summary:
        raise CommandError(f"{path.name}: need title, date, extra.category, extra.summary")
    if category not in CATEGORY_SLUGS:
        raise CommandError(f"{path.name}: unknown category {category!r}")

    if isinstance(raw_date, datetime):
        published = raw_date.date()
    elif isinstance(raw_date, date):
        published = raw_date
    else:
        published = date.fromisoformat(str(raw_date))

    tags = extra.get("tags") or []
    if isinstance(tags, list):
        tags_text = ", ".join(str(tag) for tag in tags)
    else:
        tags_text = str(tags)

    return {
        "slug": path.stem,
        "title": title,
        "published_at": published,
        "category": category,
        "summary": summary,
        "tags": tags_text,
        "body": text[end + 5 :].strip(),
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
            _obj, was_created = Post.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "published_at": data["published_at"],
                    "category": data["category"],
                    "summary": data["summary"],
                    "body": data["body"],
                    "tags": data["tags"],
                    "is_published": True,
                },
            )
            created += was_created
            updated += not was_created
            self.stdout.write(f"{'created' if was_created else 'updated'}: {data['slug']}")
        self.stdout.write(self.style.SUCCESS(f"done: +{created} ~{updated}"))
