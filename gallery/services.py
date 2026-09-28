from .models import GalleryCategory, GalleryPhoto


class GalleryService:

    @classmethod
    def get_categories(cls):
        return GalleryCategory.objects.all()

    @classmethod
    def get_published_photos(cls):
        return (
            GalleryPhoto.objects
            .filter(is_published=True)
            .select_related("category")
            .order_by("order", "-created_at")
        )

    @classmethod
    def get_featured_photos(cls, limit=6):
        return (
            GalleryPhoto.objects
            .filter(
                is_published=True,
                is_featured=True,
            )
            .select_related("category")
            .order_by("order", "-created_at")[:limit]
        )

    @classmethod
    def get_photos_by_category(cls, category_slug):
        return (
            GalleryPhoto.objects
            .filter(
                is_published=True,
                category__slug=category_slug,
            )
            .select_related("category")
            .order_by("order", "-created_at")
        )