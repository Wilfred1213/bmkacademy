from django.contrib import admin

from .models import (
    AcademicYear,
    Term,
    SchoolClass,
    Subject,
    ClassSubject
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_current",
    )

    list_filter = (
        "is_current",
    )

    search_fields = (
        "name",
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):

    list_display = (
        "academic_year",
        "name",
        "start_date",
        "end_date",
        "is_current",
    )

    list_filter = (
        "academic_year",
        "is_current",
    )

    search_fields = (
        "academic_year__name",
    )


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "section",
    )

    list_filter = (
        "section",
    )

    search_fields = (
        "name",
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):

    list_display = (
        "school_class",
        "subject",
        "is_active",
    )

    list_filter = (
        "school_class",
        "is_active",
    )

    search_fields = (
        "school_class__name",
        "subject__name",
        "subject__code",
    )