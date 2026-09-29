"""ASCII slugs safe for Django path converters (<slug:>)."""

from __future__ import annotations

import re

from django.utils.text import slugify

_RU = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "i",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}

# Django's <slug:> accepts [-a-zA-Z0-9_]
_SLUG_OK = re.compile(r"^[-a-zA-Z0-9_]+$")


def transliterate_ru(text: str) -> str:
    out: list[str] = []
    for ch in text:
        lower = ch.lower()
        if lower in _RU:
            out.append(_RU[lower])
        else:
            out.append(ch)
    return "".join(out)


def ascii_slug(title: str) -> str:
    base = slugify(transliterate_ru(title), allow_unicode=False) or "post"
    if not _SLUG_OK.match(base):
        return "post"
    return base


def unique_slug(title: str, *, exclude_pk: int | None = None) -> str:
    from .models import Post

    base = ascii_slug(title)
    slug = base
    n = 2
    qs = Post.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


def is_url_safe_slug(slug: str) -> bool:
    return bool(slug) and bool(_SLUG_OK.match(slug))
