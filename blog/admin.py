from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_at", "is_published")
    list_filter = ("category", "is_published", "published_at")
    search_fields = ("title", "summary", "body")
    date_hierarchy = "published_at"
    view_on_site = True
    readonly_fields = ("slug", "published_at")
