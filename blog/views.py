from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Category, Post


def _published_posts():
    # select_related — иначе лента и категория устроят N+1 по category
    return Post.objects.filter(is_published=True).select_related("category")


@require_GET
def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    posts = _published_posts()[:20]
    return render(request, "blog/home.html", {"posts": posts})


@require_GET
def category(request: HttpRequest, slug: str) -> HttpResponse:
    cat = get_object_or_404(Category, slug=slug)
    posts = _published_posts().filter(category=cat)
    return render(
        request,
        "blog/category.html",
        {"category": cat, "posts": posts},
    )


@require_GET
def post_detail(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(_published_posts(), slug=slug)
    return render(request, "blog/post.html", {"post": post})
