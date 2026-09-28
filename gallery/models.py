from django.db import models

from django.utils.text import slugify


class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GalleryPhoto(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.PROTECT,
        related_name="photos",
    )
    image = models.ImageField(upload_to="gallery/")
    caption = models.TextField(blank=True)

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title