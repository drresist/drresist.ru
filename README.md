# DrResist.ru

Личный блог на Django. Посты хранятся в БД (admin или импорт Markdown из `posts/`).

## Стек

- Django 5.1, Markdown в теле поста
- Категории: IT / Health / Sport
- Локально — SQLite; в проде — Postgres через `DATABASE_URL`
- Healthcheck: `GET /health` → `{"status":"ok"}`

## Локально

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Импорт старых `.md` из `posts/` (идемпотентно по slug):

```sh
python manage.py import_posts
```

Тесты:

```sh
python manage.py test blog
```

## URL

| Путь | Назначение |
|------|------------|
| `/` | лента |
| `/category/<slug>/` | раздел |
| `/posts/<slug>/` | пост |
| `/health` | healthcheck |
| `/admin/` | Django admin |

## Env

- `DJANGO_SECRET_KEY` — обязателен в проде
- `DJANGO_DEBUG` — `1`/`0` (по умолчанию `1`)
- `DJANGO_ALLOWED_HOSTS` — через запятую
- `DATABASE_URL` — `postgres://...` или пусто (sqlite)

Шаблон Markdown-поста: [POST_TEMPLATE.md](POST_TEMPLATE.md).

## Docker and CI

Django app entrypoint: `config.wsgi`, health at `GET /health` (no trailing slash).

```sh
# local with Postgres
docker compose up --build
# then http://127.0.0.1:8000/health

# import markdown from posts/
python manage.py import_posts
```

GitHub Actions (`deploy/github-ci.yml` (скопировать в `.github/workflows/ci.yml` — нужен scope `workflow`)) runs migrations, `import_posts`, `manage.py test blog`, then builds the image and checks `/health`.

Deploy credentials and Caddy/host wiring stay with ops — not in this repo.

