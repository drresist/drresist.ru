import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def render_markdown(value: str) -> str:
    if not value:
        return ""
    return mark_safe(
        md.markdown(
            value,
            extensions=["fenced_code", "tables", "nl2br"],
        )
    )
