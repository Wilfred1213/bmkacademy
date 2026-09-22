import uuid
from django.utils import timezone
from .email_service import NotificationEmailService
from .models import Notification


class NotificationService:

    @classmethod
    def create_notification(
        cls,
        recipient,
        title,
        message,
        notification_type="general",
        link="",
    ):
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )


    @classmethod
    def send_announcement(
        cls,
        title,
        message,
        recipients,
        recipient_group="",
        notification_type="announcement",
        link="",
    ):
        recipients = list(recipients)

        # One ID for this entire announcement
        announcement_id = uuid.uuid4()

        notifications = [
            Notification(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                recipient_group=recipient_group,
                announcement_id=announcement_id,
                link=link,
            )
            for recipient in recipients
        ]

        created_notifications = Notification.objects.bulk_create(
            notifications
        )

        # Send email separately to each recipient
        for recipient in recipients:
            NotificationEmailService.send_announcement_email(
                recipient=recipient,
                title=title,
                message=message,
            )

        return created_notifications

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


