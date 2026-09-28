# DrResist.ru

Static Russian language personal blog. Articles are Markdown files committed to `posts/`; Zola validates and builds them into static pages.

## Requirements

- [Zola](https://www.getzola.org/documentation/getting-started/overview/)
- Rust and Cargo (the small metadata validator is built on the first run)

## Write a post

Copy the [post template](POST_TEMPLATE.md) to `posts/my-post.md`. Keep the filename lowercase kebab-case; it becomes the stable URL `/posts/my-post/`.

Required metadata:

- `title`: non-empty string
- `date`: valid TOML date in `YYYY-MM-DD` form
- `extra.category`: `it`, `health`, or `sport`
- `extra.summary`: non-empty string
- `extra.tags`: optional list of non-empty strings

The filename, metadata, and duplicate slugs are checked before Zola builds the site. Validation errors include the file name and reason.

The Markdown body supports Russian text, headings, lists, links, images, blockquotes, and fenced code blocks. Put shared images in `static/images/` and reference them as `/images/file-name.png`.

Each post page includes its title, publication date, category, summary, optional tags, and canonical URL. Unknown paths use the generated `dist/404.html` page. To serve it with HTTP status 404 on Caddy, configure the site block to route errors to that file:

```caddyfile
handle_errors 404 {
    rewrite /404.html
    file_server
}
```

Keep this handler inside the existing site block, alongside the site's `root` and `file_server` directives. Caddy preserves the 404 status while serving the custom page.

## Preview and build

Start a local preview:

```sh
bash scripts/site serve
```

Open <http://127.0.0.1:1111>. The command validates posts, stages them for Zola, and starts its preview server. Rerun it after adding or removing a post.

Build production files into `dist/`:

```sh
bash scripts/site build
```

Check Zola's content and links:

```sh
bash scripts/site check
```

## Hosting

The public page is served from CloudCode by Caddy. This repository is the local source for the site; it is separate from the retired `wbtsre_blog` project. The generated `dist/` directory is the static site output.
