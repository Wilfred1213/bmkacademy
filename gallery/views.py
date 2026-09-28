from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import GalleryCategory, GalleryPhoto
from .services import GalleryService


def gallery(request):
    photos = GalleryService.get_published_photos()
    categories = GalleryService.get_categories()

    paginator = Paginator(photos, 12)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "gallery/gallery.html",
        {
            "photos": page_obj,
            "page_obj": page_obj,
            "categories": categories,
        },
    )


def category_gallery(request, slug):
    category = get_object_or_404(
        GalleryCategory,
        slug=slug,
    )

    photos = GalleryService.get_photos_by_category(
        category_slug=slug
    )

    paginator = Paginator(photos, 12)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "gallery/category_gallery.html",
        {
            "category": category,
            "photos": page_obj,
            "page_obj": page_obj,
            "categories": GalleryService.get_categories(),
        },
    )


def photo_detail(request, pk):
    photo = get_object_or_404(
        GalleryPhoto.objects.select_related("category"),
        pk=pk,
        is_published=True,
    )

    return render(
        request,
        "gallery/photo_detail.html",
        {
            "photo": photo,
        },
    )