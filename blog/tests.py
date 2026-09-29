from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Category, Post


class BlogSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.it, _ = Category.objects.get_or_create(slug="it", defaults={"name": "IT"})
        Category.objects.get_or_create(slug="health", defaults={"name": "Health"})
        Category.objects.get_or_create(slug="sport", defaults={"name": "Sport"})
        cls.post = Post.objects.create(
            title="Тестовый пост",
            slug="test-post",
            published_at=date(2026, 9, 29),
            category=cls.it,
            summary="Кратко",
            body="## Заголовок\n\nТекст **жирный**.",
            tags=["тест"],
            is_published=True,
        )
        Post.objects.create(
            title="Черновик",
            slug="draft",
            published_at=date(2026, 9, 28),
            category=cls.it,
            summary="скрыт",
            body="no",
            is_published=False,
        )

    def test_health(self):
        r = self.client.get(reverse("blog:health"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_home_lists_published_only(self):
        r = self.client.get(reverse("blog:home"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Тестовый пост")
        self.assertNotContains(r, "Черновик")

    def test_category(self):
        r = self.client.get(reverse("blog:category", kwargs={"slug": "it"}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Тестовый пост")

    def test_post_renders_markdown(self):
        r = self.client.get(reverse("blog:post", kwargs={"slug": "test-post"}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "<strong>жирный</strong>")
        self.assertContains(r, "<h2>Заголовок</h2>")

    def test_queries_home_no_n_plus_one(self):
        with self.assertNumQueries(2):
            self.client.get(reverse("blog:home"))
