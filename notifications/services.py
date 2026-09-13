from django.utils import timezone

from .models import Notification


class NotificationService:

    @classmethod
    def create_notification(
        cls,
        recipient,
        title,
        message,
        notification_type="general",
    ):
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
        )

    @classmethod
    def mark_as_read(cls, notification):
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(
                update_fields=[
                    "is_read",
                    "read_at",
                ]
            )

        return notification

    @classmethod
    def mark_all_as_read(cls, user):
        return Notification.objects.filter(
            recipient=user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )

    @classmethod
    def get_unread_count(cls, user):
        return Notification.objects.filter(
            recipient=user,
            is_read=False,
        ).count()

    @classmethod
    def get_user_notifications(cls, user):
        return Notification.objects.filter(
            recipient=user,
        )