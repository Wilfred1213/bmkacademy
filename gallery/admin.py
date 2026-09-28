from django.contrib import admin

from .models import GalleryCategory, GalleryPhoto


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_featured",
        "is_published",
        "order",
        "created_at",
    )

    list_filter = (
        "category",
        "is_featured",
        "is_published",
        "created_at",
    )

    search_fields = (
        "title",
        "caption",
        "category__name",
    )

    list_editable = (
        "is_featured",
        "is_published",
        "order",
    )

    ordering = (
        "order",
        "-created_at",
    )