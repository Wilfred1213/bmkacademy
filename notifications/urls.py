from django.urls import path

from . import views


app_name = "notifications"


urlpatterns = [

    path(
        "",
        views.notification_list,
        name="notification_list",
    ),

    path(
        "<int:notification_id>/read/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),

    path(
        "mark-all-read/",
        views.mark_all_notifications_as_read,
        name="mark_all_notifications_as_read",
    ),
    path(
    "announcements/create/",
    views.create_announcement,
    name="create_announcement",
    ),
    path(
    "announcements/",
    views.announcement_history,
    name="announcement_history",
    ),
    path(
    "announcements/<uuid:announcement_id>/",
    views.announcement_detail,
    name="announcement_detail",
),
]