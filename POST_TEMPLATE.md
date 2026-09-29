+++
title = "Заголовок заметки"
date = 2026-09-29

[extra]
category = "it" # it, health, or sport
summary = "Краткое описание заметки."
tags = ["пример"] # optional
+++

Текст заметки в Markdown. Импорт в БД:

```sh
python manage.py import_posts
```

Имя файла (`my-post.md`) становится slug URL `/posts/my-post/`.
