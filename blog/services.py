from django.utils import timezone
from django.db.models import Q
from .models import Category, Post, Comment


class BlogService:

    @classmethod
    def create_category(cls, name, description=""):
        return Category.objects.create(
            name=name,
            description=description,
        )

    @classmethod
    def create_post(
        cls,
        title,
        category,
        author,
        content,
        excerpt="",
        featured_image=None,
        status="draft",
    ):
        post = Post(
            title=title,
            category=category,
            author=author,
            content=content,
            excerpt=excerpt,
            featured_image=featured_image,
            status=status,
        )

        if status == "published":
            post.published_at = timezone.now()

        post.save()

        return post

    @classmethod
    def publish_post(cls, post):
        post.status = "published"
        post.published_at = timezone.now()

        post.save(
            update_fields=[
                "status",
                "published_at",
                "updated_at",
            ]
        )

        return post

    @classmethod
    def unpublish_post(cls, post):
        post.status = "draft"
        post.published_at = None

        post.save(
            update_fields=[
                "status",
                "published_at",
                "updated_at",
            ]
        )

        return post

    @classmethod
    def get_published_posts(cls):
        return (
            Post.objects
            .filter(status="published")
            .select_related("category", "author")
            .order_by("-published_at")
        )

    
    @classmethod
    def create_comment(
        cls,
        post,
        name,
        email,
        message,
    ):
        return Comment.objects.create(
            post=post,
            name=name,
            email=email,
            message=message,
        )


    @classmethod
    def get_approved_comments(cls, post):
        return (
            post.comments
            .filter(is_approved=True)
            .order_by("created_at")
        )
    
    @classmethod
    def get_published_posts_by_category(cls, category_slug):

        return (
            Post.objects
            .filter(
                status="published",
                category__slug=category_slug,
            )
            .select_related(
                "category",
                "author",
            )
            .order_by("-published_at")
        )
    
    @classmethod
    def get_published_posts(cls, search_query=""):

        posts = (
            Post.objects
            .filter(status="published")
            .select_related("category", "author")
            .order_by("-published_at")
        )

        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query)
                | Q(excerpt__icontains=search_query)
                | Q(content__icontains=search_query)
            )

        return posts

    @classmethod
    def get_related_posts(cls, post, limit=3):

        return (
            Post.objects
            .filter(
                status="published",
                category=post.category,
            )
            .exclude(
                id=post.id,
            )
            .select_related(
                "category",
                "author",
            )
            .order_by("-published_at")[:limit]
        )

    @classmethod
    def get_latest_posts(cls, limit=3):
        return (
            Post.objects
            .filter(status="published")
            .select_related("category", "author")
            .order_by("-published_at")[:limit]
        )