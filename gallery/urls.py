from django.urls import path

from . import views


app_name = "gallery"


urlpatterns = [
    path("", views.gallery, name="gallery"),
    path(
        "category/<slug:slug>/",
        views.category_gallery,
        name="category_gallery",
    ),
    path(
        "photo/<int:pk>/",
        views.photo_detail,
        name="photo_detail",
    ),
]