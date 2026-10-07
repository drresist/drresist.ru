from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Post


class BlogSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create(
            title="Тестовый пост",
            slug="test-post",
            published_at=date(2026, 9, 29),
            category="it",
            summary="Кратко",
            body="## Заголовок\n\nТекст **жирный**.",
            tags="тест",
            is_published=True,
        )
        Post.objects.create(
            title="Черновик",
            slug="draft",
            published_at=date(2026, 9, 28),
            category="it",
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

    def test_unknown_category_404(self):
        r = self.client.get(reverse("blog:category", kwargs={"slug": "nope"}))
        self.assertEqual(r.status_code, 404)

    def test_post_renders_markdown(self):
        r = self.client.get(reverse("blog:post", kwargs={"slug": "test-post"}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "<strong>жирный</strong>")
        self.assertContains(r, "<h2>Заголовок</h2>")

    def test_queries_home_no_n_plus_one(self):
        with self.assertNumQueries(1):
            self.client.get(reverse("blog:home"))


class BlogUiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Post.objects.create(
            title="Видимый",
            slug="visible-ui",
            published_at=date(2026, 9, 29),
            category="it",
            summary="Краткое описание для карточки",
            body="Текст",
            is_published=True,
        )

    def test_nav_links_all_categories(self):
        r = self.client.get(reverse("blog:home"))
        self.assertEqual(r.status_code, 200)
        for slug, name in (("it", "IT"), ("health", "Health"), ("sport", "Sport")):
            self.assertContains(r, name)
            self.assertContains(r, reverse("blog:category", kwargs={"slug": slug}))

    def test_home_card_shows_title_date_category_summary(self):
        r = self.client.get(reverse("blog:home"))
        self.assertContains(r, "Видимый")
        self.assertContains(r, "2026-09-29")
        self.assertContains(r, "IT")
        self.assertContains(r, "Краткое описание для карточки")
        self.assertContains(r, reverse("blog:post", kwargs={"slug": "visible-ui"}))

    def test_empty_category_useful_state(self):
        r = self.client.get(reverse("blog:category", kwargs={"slug": "health"}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "пока пусто")
        self.assertContains(r, reverse("blog:home"))

    def test_category_aria_current(self):
        r = self.client.get(reverse("blog:category", kwargs={"slug": "it"}))
        self.assertContains(r, 'aria-current="page"')


class PostAdminTests(TestCase):
    def test_admin_create_sets_slug_date_and_tags(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_superuser("editor", "e@example.com", "x")
        self.client.force_login(user)
        r = self.client.post(
            reverse("admin:blog_post_add"),
            {
                "title": "Новый пост",
                "category": "it",
                "summary": "кратко",
                "body": "# hi\n\ntext",
                "tags": "django, blog",
                "is_published": "on",
            },
            follow=True,
        )
        self.assertEqual(r.status_code, 200)
        post = Post.objects.get(title="Новый пост")
        self.assertTrue(post.slug)
        self.assertEqual(post.published_at, date.today())
        self.assertEqual(post.tag_list(), ["django", "blog"])
        self.assertTrue(post.is_published)


class AsciiSlugTests(TestCase):
    def test_cyrillic_title_makes_ascii_slug(self):
        from .slugs import ascii_slug

        self.assertEqual(ascii_slug("Что такое SRE"), "chto-takoe-sre")
        self.assertRegex(ascii_slug("Привет мир"), r"^[a-z0-9-]+$")

    def test_post_with_cyrillic_title_reverses(self):
        post = Post(
            title="Что такое SRE",
            published_at=date(2026, 9, 29),
            category="it",
            summary="s",
            body="b",
            is_published=True,
        )
        post.save()
        self.assertRegex(post.slug, r"^[-a-zA-Z0-9_]+$")
        r = self.client.get(reverse("blog:post", kwargs={"slug": post.slug}))
        self.assertEqual(r.status_code, 200)

    def test_home_survives_cyrillic_titled_post(self):
        Post.objects.create(
            title="Что такое SRE",
            slug="bad-will-be-fixed",
            published_at=date(2026, 9, 29),
            category="it",
            summary="s",
            body="b",
            is_published=True,
        )
        bad = Post(
            title="Ещё один",
            published_at=date(2026, 9, 29),
            category="it",
            summary="s",
            body="b",
            is_published=True,
        )
        bad.slug = "ещё-один"
        bad.save()
        self.assertRegex(bad.slug, r"^[-a-zA-Z0-9_]+$")
        r = self.client.get(reverse("blog:home"))
        self.assertEqual(r.status_code, 200)
