from .models import CATEGORIES


def nav_categories(request):
    return {
        "nav_categories": [{"slug": slug, "name": name} for slug, name in CATEGORIES],
    }
