from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from django.core.paginator import Paginator
from .forms import CategoryForm, PostForm, CommentForm
from .models import Category, Post
from .services import BlogService


@login_required
@role_required("admin")
def create_category(request):

    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():

            BlogService.create_category(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )

            messages.success(
                request,
                "Category created successfully.",
            )

            return redirect("blog:category_list")

    else:
        form = CategoryForm()

    return render(
        request,
        "blog/create_category.html",
        {
            "form": form,
        },
    )


@login_required
@role_required("admin")
def create_post(request):

    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            BlogService.create_post(
                title=form.cleaned_data["title"],
                category=form.cleaned_data["category"],
                author=request.user,
                content=form.cleaned_data["content"],
                excerpt=form.cleaned_data["excerpt"],
                featured_image=form.cleaned_data["featured_image"],
                status=form.cleaned_data["status"],
            )

            messages.success(
                request,
                "Blog post created successfully.",
            )

            return redirect("blog:post_list")

    else:
        form = PostForm()

    return render(
        request,
        "blog/create_post.html",
        {
            "form": form,
        },
    )


def post_list(request):

    search_query = request.GET.get("q", "").strip()

    posts = BlogService.get_published_posts(
        search_query=search_query
    )

    paginator = Paginator(posts, 6)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    categories = Category.objects.order_by("name")

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": page_obj,
            "categories": categories,
            "page_obj": page_obj,
            "search_query": search_query,
        },
    )


def post_detail(request, slug):

    post = get_object_or_404(
        Post.objects.select_related(
            "category",
            "author",
        ),
        slug=slug,
        status="published",
    )

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            BlogService.create_comment(
                post=post,
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                message=form.cleaned_data["message"],
            )

            messages.success(
                request,
                "Thank you for your comment. "
                "Your comment has been submitted for review.",
            )

            return redirect(
                "blog:post_detail",
                slug=post.slug,
            )

    else:

        form = CommentForm()

    comments = BlogService.get_approved_comments(post)

    related_posts = BlogService.get_related_posts(post)

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": form,
            "related_posts": related_posts,
        },
    )


@login_required
@role_required("admin")
def category_list(request):

    categories = Category.objects.order_by("name")

    return render(
        request,
        "blog/category_list.html",
        {
            "categories": categories,
        },
    )



def category_posts(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug,
    )

    posts = BlogService.get_published_posts_by_category(
        category_slug=slug
    )

    paginator = Paginator(posts, 6)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/category_posts.html",
        {
            "category": category,
            "posts": page_obj,
            "page_obj": page_obj,
        },
    )
