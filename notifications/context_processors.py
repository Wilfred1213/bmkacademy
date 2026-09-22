from .services import NotificationService

def notification_context(request):

    
    if not request.user.is_authenticated:
        return {
            "notification_unread_count": 0,
            "latest_notifications": [],
        }

    notifications = (
        NotificationService
        .get_user_notifications(request.user)
        .order_by("-created_at")[:3]
    )

    unread_count = (
        NotificationService
        .get_unread_count(request.user)
    )

    return {
        "notification_unread_count": unread_count,
        "latest_notifications": notifications,
    }

