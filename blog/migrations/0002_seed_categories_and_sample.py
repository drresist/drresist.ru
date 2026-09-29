from datetime import date

from django.db import migrations


def seed(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    Post = apps.get_model("blog", "Post")
    cats = {
        "it": "IT",
        "health": "Health",
        "sport": "Sport",
    }
    for slug, name in cats.items():
        Category.objects.get_or_create(slug=slug, defaults={"name": name})
    it = Category.objects.get(slug="it")
    Post.objects.get_or_create(
        slug="hello-django",
        defaults={
            "title": "Блог на Django",
            "published_at": date(2026, 9, 29),
            "category": it,
            "summary": "Первый пост после переезда со статики на Django.",
            "body": (
                "Сайт теперь отдаёт страницы из Django, а не из Zola.\n\n"
                "- посты в БД\n"
                "- Markdown в теле\n"
                "- разделы IT / Health / Sport\n"
            ),
            "tags": ["meta"],
            "is_published": True,
        },
    )


def unseed(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    Post.objects.filter(slug="hello-django").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
