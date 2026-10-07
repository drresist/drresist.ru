from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import CATEGORIES, Post
from .repo_history import load_history

CATEGORY_NAMES = dict(CATEGORIES)


def _published_posts():
    return Post.objects.filter(is_published=True)


@require_GET
def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    history = load_history(settings.BASE_DIR)
    commits = history["commits"]
    return render(
        request,
        "blog/home.html",
        {
            "posts": _published_posts()[:20],
            "repo_updated": commits[0]["date"] if commits else "",
            "commits": commits,
        },
    )


@require_GET
def category(request: HttpRequest, slug: str) -> HttpResponse:
    name = CATEGORY_NAMES.get(slug)
    if name is None:
        raise Http404
    posts = _published_posts().filter(category=slug)
    return render(
        request,
        "blog/category.html",
        {"category": {"slug": slug, "name": name}, "posts": posts},
    )


@require_GET
def post_detail(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(_published_posts(), slug=slug)
    return render(request, "blog/post.html", {"post": post})
