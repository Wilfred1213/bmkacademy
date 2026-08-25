from django.contrib import admin

from .models import Student, Enrollment


# admin.site.register(Student)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "admission_number",
        "status",
    )

    search_fields = (
        "first_name",
        "middle_name",
        "last_name",
        "admission_number",
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "academic_year",
        "term",
        "school_class",
        "is_current",
    )

    list_filter = (
        "academic_year",
        "term",
        "school_class",
        "is_current",
    )

    search_fields = (
        "student__first_name",
        "student__middle_name",
        "student__last_name",
        "student__admission_number",
    )

    autocomplete_fields = (
        "student",
        "academic_year",
        "term",
        "school_class",
    )