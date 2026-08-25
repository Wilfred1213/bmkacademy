from django.contrib import admin

from .models import (
    Teacher,
    TeachingAssignment,
    ClassTeacherAssignment,
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "user",
        "qualification",
        "phone",
        "date_joined",
        "is_active",
    )

    list_filter = (
        "is_active",
        "qualification",
    )

    search_fields = (
        "employee_id",
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__email",
    )


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "teacher",
        "class_subject",
        "academic_year",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "is_active",
    )

    search_fields = (
        "teacher__employee_id",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "class_subject__school_class__name",
        "class_subject__subject__name",
        "academic_year__name",
    )


@admin.register(ClassTeacherAssignment)
class ClassTeacherAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "teacher",
        "school_class",
        "academic_year",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "is_active",
    )

    search_fields = (
        "teacher__employee_id",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "school_class__name",
        "academic_year__name",
    )