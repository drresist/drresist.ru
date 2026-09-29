from django.db import models
from django.urls import reverse


class Category(models.Model):
    slug = models.SlugField(unique=True, max_length=32)
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ["slug"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("blog:category", kwargs={"slug": self.slug})


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    published_at = models.DateField(db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    summary = models.TextField()
    body = models.TextField(help_text="Markdown")
    tags = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-pk"]

    def __str__(self) -> str:
        return self.title


    def save(self, *args, **kwargs):
        from .slugs import ascii_slug, is_url_safe_slug, unique_slug

        if not self.slug or not is_url_safe_slug(self.slug):
            self.slug = unique_slug(self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("blog:post", kwargs={"slug": self.slug})
