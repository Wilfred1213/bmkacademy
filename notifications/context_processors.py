from .services import NotificationService


def notification_context(request):

    if request.user.is_authenticated:

        unread_count = NotificationService.get_unread_count(
            request.user
        )

    else:

        unread_count = 0

    return {
        "notification_unread_count": unread_count,
    }