from django.contrib import admin

from .models import (
    AssessmentComponent,
    AssessmentScore,
    BehaviourCategory,
    StudentBehaviourRating,
    StudentSubjectResult,
    StudentTermReport
)

@admin.register(AssessmentComponent)
class AssessmentComponentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "term",
        "max_score",
        "order",
        "is_active",
    )

    list_filter = (
        "term__academic_year",
        "term",
        "is_active",
    )

    search_fields = (
        "name",
        "term__academic_year__name",
    )

    ordering = (
        "term",
        "order",
    )

class AssessmentScoreInline(admin.TabularInline):

    model = AssessmentScore

    extra = 0

    autocomplete_fields = (
        "assessment_component",
    )

@admin.register(StudentSubjectResult)
class StudentSubjectResultAdmin(admin.ModelAdmin):

    list_display = (
        "enrollment",
        "class_subject",
        "total_score",
        "grade",
    )

    list_filter = (
        "enrollment__academic_year",
        "enrollment__term",
        "enrollment__school_class",
        "class_subject",
    )

    search_fields = (
        "enrollment__student__first_name",
        "enrollment__student__last_name",
        "enrollment__student__admission_number",
        "class_subject__subject__name",
    )

    autocomplete_fields = (
        "enrollment",
        "class_subject",
    )

    readonly_fields = (
        "total_score",
        "grade",
        "remark",
    )

    inlines = (
        AssessmentScoreInline,
    )

@admin.register(BehaviourCategory)
class BehaviourCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "order",
        "name",
    )

@admin.register(StudentBehaviourRating)
class StudentBehaviourRatingAdmin(admin.ModelAdmin):

    list_display = (
        "enrollment",
        "behaviour_category",
        "rating",
    )

    list_filter = (
        "enrollment__academic_year",
        "enrollment__term",
        "enrollment__school_class",
    )

    search_fields = (
        "enrollment__student__first_name",
        "enrollment__student__last_name",
        "enrollment__student__admission_number",
        "behaviour_category__name",
    )

    autocomplete_fields = (
        "enrollment",
        "behaviour_category",
    )

@admin.register(StudentTermReport)
class StudentTermReportAdmin(admin.ModelAdmin):

    list_display = (
        "enrollment",
        "next_term_begins",
        "is_published",
    )

    search_fields = (
        "enrollment__student__first_name",
        "enrollment__student__middle_name",
        "enrollment__student__last_name",
    )

    list_filter = (
        "is_published",
        "enrollment__academic_year",
        "enrollment__term",
        "enrollment__school_class",
    )