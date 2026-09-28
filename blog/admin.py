from django.contrib import admin
from .services import BlogService
from .models import Category, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "created_at",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "author",
        "publication_status",
        "published_at",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
        "excerpt",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
        "published_at",
    )

    actions = [
        "publish_posts",
        "unpublish_posts",
    ]

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):

        for post in queryset:
            BlogService.publish_post(post)

    @admin.action(description="Move selected posts to draft")
    def unpublish_posts(self, request, queryset):

        for post in queryset:
            BlogService.unpublish_post(post)

    
    @admin.display(description="Publication Status")
    def publication_status(self, obj):

        if obj.status == "published":
            return "Published"

        return "Draft"



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "post",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "message",
        "post__title",
    )

    actions = [
        "approve_comments",
        "unapprove_comments",
    ]

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):

        queryset.update(
            is_approved=True
        )

    @admin.action(description="Unapprove selected comments")
    def unapprove_comments(self, request, queryset):

        queryset.update(
            is_approved=False
        )
