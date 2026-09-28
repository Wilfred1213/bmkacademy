from django.urls import path

from . import views


app_name = "blog"


urlpatterns = [
    path(
        "",
        views.post_list,
        name="post_list",
    ),

    path(
        "post/<slug:slug>/",
        views.post_detail,
        name="post_detail",
    ),

    path(
        "create/",
        views.create_post,
        name="create_post",
    ),

    path(
        "categories/",
        views.category_list,
        name="category_list",
    ),

    path(
        "categories/create/",
        views.create_category,
        name="create_category",
    ),
    path(
    "category/<slug:slug>/",
    views.category_posts,
    name="category_posts",
),
]