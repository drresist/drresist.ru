# DrResist.ru

Личный блог на Django. Посты в БД (Django admin или импорт Markdown из `posts/`).

## Стек

- Django 5.1, Markdown в теле поста
- Категории: IT / Health / Sport
- Локально — SQLite; в проде — Postgres (`DATABASE_URL`)
- Gunicorn + WhiteNoise в Docker; Caddy снаружи
- Healthcheck: `GET /health` → `{"status":"ok"}`

## Локально

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_posts   # опционально: posts/*.md
python manage.py createsuperuser
python manage.py runserver
```

Открыть: http://127.0.0.1:8000/ и http://127.0.0.1:8000/admin/

Тесты:

```sh
python manage.py test blog
```

## Docker

```sh
docker compose up --build
# http://127.0.0.1:8000/health
```

Entrypoint: migrate → `import_posts` → collectstatic → gunicorn `:8000`.

Шаблон CI (нужен GitHub token со scope `workflow`, чтобы положить в Actions):
[`deploy/github-ci.yml`](deploy/github-ci.yml).

## URL

| Путь | Назначение |
|------|------------|
| `/` | лента |
| `/category/<slug>/` | раздел (it / health / sport) |
| `/posts/<slug>/` | пост |
| `/health` | healthcheck |
| `/admin/` | Django admin |

## Markdown → БД

Файлы в `posts/*.md` с TOML frontmatter (`+++`). Шаблон: [POST_TEMPLATE.md](POST_TEMPLATE.md).

```sh
python manage.py import_posts
```

Идемпотентно по slug (имя файла). Источник правды после импорта — БД/admin.

## Env

| Переменная | Назначение |
|------------|------------|
| `DJANGO_SECRET_KEY` | обязателен в проде |
| `DJANGO_DEBUG` | `1` / `0` (по умолчанию `1`) |
| `DJANGO_ALLOWED_HOSTS` | через запятую |
| `DATABASE_URL` | `postgres://...` или пусто → sqlite |
| `GUNICORN_WORKERS` | опционально, по умолчанию `2` |
