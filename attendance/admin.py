# attendance/admin.py

from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "attendance_date",
        "status",
    )

    list_filter = (
        "status",
        "attendance_date",
    )

    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__admission_number",
    )