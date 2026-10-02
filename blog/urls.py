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
    path(
    "manage/",
    views.manage_posts,
    name="manage_posts",
    ),
    path(
    "manage/<int:post_id>/edit/",
    views.edit_post,
    name="edit_post",
    ),
    path(
    "manage/<int:post_id>/publish/",
    views.publish_post,
    name="publish_post",
    ),

    path(
        "manage/<int:post_id>/unpublish/",
        views.unpublish_post,
        name="unpublish_post",
    ),
    path(
    "manage/<int:post_id>/delete/",
    views.delete_post,
    name="delete_post",
),
]