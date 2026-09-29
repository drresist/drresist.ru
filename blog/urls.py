from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("health", views.health, name="health"),
    path("category/<slug:slug>/", views.category, name="category"),
    path("posts/<slug:slug>/", views.post_detail, name="post"),
]
