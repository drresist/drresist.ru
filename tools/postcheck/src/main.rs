use std::{
    collections::HashSet,
    env,
    error::Error,
    fs,
    path::{Path, PathBuf},
};

type Result<T> = std::result::Result<T, Box<dyn Error>>;

fn fail(path: &Path, reason: impl AsRef<str>) -> Box<dyn Error> {
    format!("{}: {}", path.display(), reason.as_ref()).into()
}

fn valid_slug(slug: &str) -> bool {
    !slug.is_empty()
        && slug.split('-').all(|part| {
            !part.is_empty()
                && part
                    .bytes()
                    .all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit())
        })
}

fn valid_date(value: &str) -> bool {
    let Some((year, month_day)) = value.split_once('-') else {
        return false;
    };
    let Some((month, day)) = month_day.split_once('-') else {
        return false;
    };
    if year.len() != 4 || month.len() != 2 || day.len() != 2 {
        return false;
    }
    let (Ok(year), Ok(month), Ok(day)) = (
        year.parse::<i32>(),
        month.parse::<u32>(),
        day.parse::<u32>(),
    ) else {
        return false;
    };
    let leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    let days = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if leap => 29,
        2 => 28,
        _ => return false,
    };
    day > 0 && day <= days
}

fn require_nonempty_string<'a>(
    path: &Path,
    values: &'a toml::map::Map<String, toml::Value>,
    name: &str,
) -> Result<&'a str> {
    match values.get(name).and_then(toml::Value::as_str) {
        Some(value) if !value.trim().is_empty() => Ok(value),
        _ => Err(fail(
            path,
            format!("extra.{name} must be a non-empty string"),
        )),
    }
}

fn validate(path: &Path) -> Result<()> {
    let raw = fs::read_to_string(path)?;
    let Some(after_open) = raw.strip_prefix("+++\n") else {
        return Err(fail(path, "expected TOML frontmatter starting with +++"));
    };
    let Some((frontmatter, _body)) = after_open.split_once("\n+++\n") else {
        return Err(fail(path, "expected closing +++ after frontmatter"));
    };
    let metadata: toml::Table = toml::from_str(frontmatter)
        .map_err(|error| fail(path, format!("invalid TOML frontmatter: {error}")))?;
    let root = &metadata;

    let allowed_root = ["title", "date", "extra"];
    if let Some(unknown) = root
        .keys()
        .find(|key| !allowed_root.contains(&key.as_str()))
    {
        return Err(fail(path, format!("unknown frontmatter field: {unknown}")));
    }

    if !root
        .get("title")
        .and_then(toml::Value::as_str)
        .is_some_and(|value| !value.trim().is_empty())
    {
        return Err(fail(path, "title must be a non-empty string"));
    }
    match root.get("date") {
        Some(toml::Value::Datetime(value)) if valid_date(&value.to_string()) => {}
        _ => return Err(fail(path, "date must be a valid YYYY-MM-DD TOML date")),
    }
    let extra = root
        .get("extra")
        .and_then(toml::Value::as_table)
        .ok_or_else(|| fail(path, "missing [extra] metadata table"))?;
    require_nonempty_string(path, extra, "summary")?;
    match extra.get("category").and_then(toml::Value::as_str) {
        Some("it" | "health" | "sport") => {}
        _ => {
            return Err(fail(
                path,
                "extra.category must be one of: it, health, sport",
            ))
        }
    }
    if let Some(tags) = extra.get("tags") {
        let valid = tags.as_array().is_some_and(|items| {
            items
                .iter()
                .all(|item| item.as_str().is_some_and(|tag| !tag.trim().is_empty()))
        });
        if !valid {
            return Err(fail(path, "extra.tags must be a list of non-empty strings"));
        }
    }
    let allowed = ["category", "summary", "tags"];
    if let Some(unknown) = extra.keys().find(|key| !allowed.contains(&key.as_str())) {
        return Err(fail(path, format!("unknown extra field: {unknown}")));
    }

    let slug = path
        .file_stem()
        .and_then(|name| name.to_str())
        .unwrap_or_default();
    if !valid_slug(slug) {
        return Err(fail(
            path,
            "filename must be a lowercase kebab-case slug, e.g. first-post.md",
        ));
    }
    Ok(())
}

fn run() -> Result<()> {
    let directory = env::args_os()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| "posts".into());
    if !directory.is_dir() {
        return Err(format!("{}: posts directory not found", directory.display()).into());
    }
    let mut files: Vec<PathBuf> = fs::read_dir(&directory)?
        .filter_map(std::result::Result::ok)
        .map(|entry| entry.path())
        .filter(|path| path.is_file() && path.extension().is_some_and(|ext| ext == "md"))
        .collect();
    files.sort();

    let mut slugs = HashSet::new();
    for path in &files {
        let slug = path
            .file_stem()
            .and_then(|name| name.to_str())
            .unwrap_or_default()
            .to_ascii_lowercase();
        if !slugs.insert(slug.clone()) {
            return Err(fail(path, format!("duplicate post slug: {slug}")));
        }
    }
    for path in &files {
        validate(path)?;
    }
    println!("Validated {} post(s).", files.len());
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("Post validation failed: {error}");
        std::process::exit(1);
    }
}
