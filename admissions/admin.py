from django.contrib import admin

from .models import AdmissionApplication


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "desired_class",
        "status",
        "submitted_at",
    )

    list_filter = (
        "status",
        "desired_class",
    )

    search_fields = (
        "first_name",
        "last_name",
    )