from django.db import models
from django.utils.text import slugify

class HeroSlide(models.Model):

    title = models.CharField(
        max_length=200
    )

    subtitle = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="website/hero/"
    )

    button_text = models.CharField(
        max_length=100,
        blank=True
    )

    button_url = models.CharField(
        max_length=300,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "order",
            "-created_at",
        ]


    def __str__(self):

        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"



class SchoolEvent(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    event_date = models.DateField()

    event_time = models.TimeField(
        blank=True,
        null=True
    )

    venue = models.CharField(
        max_length=200,
        blank=True
    )

    image = models.ImageField(
        upload_to="website/events/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    show_popup = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "event_date",
            "event_time",
        ]


    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(
                self.title
            )

            slug = base_slug

            counter = 2

            while SchoolEvent.objects.filter(
                slug=slug
            ).exists():

                slug = f"{base_slug}-{counter}"

                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


    def __str__(self):

        return self.title
