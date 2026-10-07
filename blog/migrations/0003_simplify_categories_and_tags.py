from django.db import migrations, models


def copy_category(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.select_related("category"):
        post.category_code = post.category.slug
        post.save(update_fields=["category_code"])


def copy_tags(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.all():
        tags = post.tags or []
        post.tags_text = ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else str(tags)
        post.save(update_fields=["tags_text"])


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_seed_categories_and_sample"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="category_code",
            field=models.CharField(default="it", max_length=16),
        ),
        migrations.RunPython(copy_category, migrations.RunPython.noop),
        migrations.RemoveField(model_name="post", name="category"),
        migrations.RenameField(
            model_name="post",
            old_name="category_code",
            new_name="category",
        ),
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.CharField(
                choices=[("it", "IT"), ("health", "Health"), ("sport", "Sport")],
                default="it",
                max_length=16,
                verbose_name="Раздел",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="tags_text",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Через запятую, например: django, devops",
                max_length=200,
                verbose_name="Теги",
            ),
        ),
        migrations.RunPython(copy_tags, migrations.RunPython.noop),
        migrations.RemoveField(model_name="post", name="tags"),
        migrations.RenameField(
            model_name="post",
            old_name="tags_text",
            new_name="tags",
        ),
        migrations.DeleteModel(name="Category"),
        migrations.AlterField(
            model_name="post",
            name="body",
            field=models.TextField(help_text="Markdown", verbose_name="Текст (Markdown)"),
        ),
        migrations.AlterField(
            model_name="post",
            name="is_published",
            field=models.BooleanField(db_index=True, default=True, verbose_name="Опубликовано"),
        ),
        migrations.AlterField(
            model_name="post",
            name="summary",
            field=models.TextField(verbose_name="Краткое"),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=200, verbose_name="Заголовок"),
        ),
    ]
