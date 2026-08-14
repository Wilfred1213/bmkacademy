from django.contrib import admin

from .models import (
    AcademicYear,
    Term,
    SchoolClass,
    Subject,
)


admin.site.register(AcademicYear)
admin.site.register(Term)
admin.site.register(SchoolClass)
admin.site.register(Subject)