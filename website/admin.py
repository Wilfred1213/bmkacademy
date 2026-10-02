from django.contrib import admin

from .models import HeroSlide, ContactMessage, SchoolEvent

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "subject",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
        "message",
    )

    readonly_fields = (
        "created_at",
    )
@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "subtitle",
    )

    ordering = (
        "order",
        "-created_at",
    )


@admin.register(SchoolEvent)
class SchoolEventAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "event_date",
        "event_time",
        "venue",
        "is_active",
        "show_popup",
    )

    list_filter = (
        "is_active",
        "show_popup",
        "event_date",
    )

    search_fields = (
        "title",
        "description",
        "venue",
    )

    ordering = (
        "event_date",
        "event_time",
    )

