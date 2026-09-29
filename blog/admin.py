from datetime import date

from django import forms
from django.contrib import admin
from django.utils.text import slugify

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class PostAdminForm(forms.ModelForm):
    tags_text = forms.CharField(
        label="Теги",
        required=False,
        help_text="Через запятую, например: django, devops",
        widget=forms.TextInput(attrs={"size": 60}),
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "category",
            "summary",
            "body",
            "tags_text",
            "is_published",
        )
        labels = {
            "title": "Заголовок",
            "category": "Раздел",
            "summary": "Краткое",
            "body": "Текст (Markdown)",
            "is_published": "Опубликовано",
        }
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3, "cols": 80}),
            "body": forms.Textarea(attrs={"rows": 24, "cols": 80}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and isinstance(self.instance.tags, list):
            self.fields["tags_text"].initial = ", ".join(self.instance.tags)

    def clean_tags_text(self) -> list[str]:
        raw = self.cleaned_data.get("tags_text") or ""
        return [t.strip() for t in raw.split(",") if t.strip()]

    def save(self, commit: bool = True) -> Post:
        post: Post = super().save(commit=False)
        post.tags = self.cleaned_data.get("tags_text") or []
        if commit:
            post.save()
        return post


def _unique_slug(title: str, exclude_pk: int | None = None) -> str:
    base = slugify(title, allow_unicode=True) or "post"
    slug = base
    n = 2
    qs = Post.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "category", "published_at", "is_published")
    list_filter = ("category", "is_published", "published_at")
    search_fields = ("title", "summary", "body")
    date_hierarchy = "published_at"
    view_on_site = True
    readonly_fields = ("slug", "published_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "category",
                    "summary",
                    "body",
                    "tags_text",
                    "is_published",
                )
            },
        ),
        (
            "Служебное",
            {
                "classes": ("collapse",),
                "fields": ("slug", "published_at"),
                "description": "Slug и дата ставятся сами. Открой, только если надо поправить.",
            },
        ),
    )

    def save_model(self, request, obj: Post, form, change) -> None:
        if not obj.published_at:
            obj.published_at = date.today()
        if not obj.slug:
            obj.slug = _unique_slug(obj.title, exclude_pk=obj.pk)
        super().save_model(request, obj, form, change)
