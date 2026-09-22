import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("general", "General"),
        ("admission", "Admission"),
        ("payment", "Payment"),
        ("result", "Result"),
        ("announcement", "Announcement"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default="general",
    )

    recipient_group = models.CharField(
        max_length=20,
        blank=True,
    )

    announcement_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    link = models.CharField(
        max_length=500,
        blank=True,
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.title}"
