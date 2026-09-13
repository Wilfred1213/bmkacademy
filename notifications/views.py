from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification
from .services import NotificationService


@login_required
def notification_list(request):

    notifications = NotificationService.get_user_notifications(
        request.user
    )

    unread_count = NotificationService.get_unread_count(
        request.user
    )

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_notification_as_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    NotificationService.mark_as_read(notification)

    return redirect("notifications:notification_list")


@login_required
def mark_all_notifications_as_read(request):

    NotificationService.mark_all_as_read(
        request.user
    )

    return redirect("notifications:notification_list")