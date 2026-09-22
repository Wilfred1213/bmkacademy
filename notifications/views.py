from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification
from .services import NotificationService

from django.db.models import Count, Min
from django.contrib import messages
from accounts.decorators import role_required
from .forms import AnnouncementForm


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

    if notification.link:
        return redirect(notification.link)

    return redirect("notifications:notification_list")
@login_required
def mark_all_notifications_as_read(request):

    NotificationService.mark_all_as_read(
        request.user
    )

    return redirect("notifications:notification_list")

@login_required
@role_required("admin")
def create_announcement(request):

    if request.method == "POST":

        form = AnnouncementForm(request.POST)

        if form.is_valid():

            title = form.cleaned_data["title"]
            message = form.cleaned_data["message"]
            recipient_group = form.cleaned_data["recipient_group"]

            User = request.user.__class__

            if recipient_group == "parents":

                recipients = User.objects.filter(
                    role="parent",
                    is_active=True,
                )

            elif recipient_group == "teachers":

                recipients = User.objects.filter(
                    role="teacher",
                    is_active=True,
                )

            elif recipient_group == "students":

                recipients = User.objects.filter(
                    role="student",
                    is_active=True,
                )

            else:

                recipients = User.objects.filter(
                    is_active=True,
                )

            notifications = NotificationService.send_announcement(
                title=title,
                message=message,
                recipients=recipients,
                recipient_group=recipient_group,
            )

            messages.success(
                request,
                f"Announcement sent successfully to "
                f"{len(notifications)} users.",
            )

            return redirect("notifications:notification_list")

    else:

        form = AnnouncementForm()

    return render(
        request,
        "notifications/create_announcement.html",
        {
            "form": form,
        },
    )


@login_required
@role_required("admin")
def announcement_history(request):

    announcements = (
        Notification.objects
        .filter(
            notification_type="announcement",
            announcement_id__isnull=False,
        )
        .values(
            "announcement_id",
            "title",
            "message",
            "recipient_group",
        )
        .annotate(
            recipient_count=Count("id"),
            sent_at=Min("created_at"),
        )
        .order_by("-sent_at")
    )

    return render(
        request,
        "notifications/announcement_history.html",
        {
            "announcements": announcements,
        },
    )

@login_required
@role_required("admin")
def announcement_detail(request, announcement_id):

    notifications = (
        Notification.objects
        .filter(
            announcement_id=announcement_id,
            notification_type="announcement",
        )
        .select_related("recipient")
        .order_by("recipient__first_name", "recipient__last_name")
    )

    if not notifications.exists():
        raise Http404("Announcement not found.")

    first_notification = notifications.first()

    return render(
        request,
        "notifications/announcement_detail.html",
        {
            "announcement": first_notification,
            "notifications": notifications,
            "recipient_count": notifications.count(),
        },
    )