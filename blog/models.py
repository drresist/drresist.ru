from datetime import date

from django.db import models
from django.urls import reverse

CATEGORIES = (
    ("it", "IT"),
    ("health", "Health"),
    ("sport", "Sport"),
)


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    published_at = models.DateField(db_index=True)
    category = models.CharField("Раздел", max_length=16, choices=CATEGORIES, default="it")
    summary = models.TextField("Краткое")
    body = models.TextField("Текст (Markdown)", help_text="Markdown")
    tags = models.CharField(
        "Теги",
        max_length=200,
        blank=True,
        default="",
        help_text="Через запятую, например: django, devops",
    )
    is_published = models.BooleanField("Опубликовано", default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-pk"]

    def __str__(self) -> str:
        return self.title

    def tag_list(self) -> list[str]:
        return [part.strip() for part in self.tags.split(",") if part.strip()]

    def save(self, *args, **kwargs):
        from .slugs import is_url_safe_slug, unique_slug

        if not self.published_at:
            self.published_at = date.today()
        if not self.slug or not is_url_safe_slug(self.slug):
            self.slug = unique_slug(self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("blog:post", kwargs={"slug": self.slug})
