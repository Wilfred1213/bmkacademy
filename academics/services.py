from django.db.models import Count, Prefetch, Q

from .models import SchoolClass, ClassSubject


class AcademicService:

    @classmethod
    def get_public_classes(cls):

        active_class_subjects = (
            ClassSubject.objects
            .filter(
                is_active=True,
                subject__is_active=True,
            )
            .select_related("subject")
        )

        classes = (
            SchoolClass.objects
            .annotate(
                public_subject_count=Count(
                    "class_subjects",
                    filter=Q(
                        class_subjects__is_active=True,
                        class_subjects__subject__is_active=True,
                    ),
                    distinct=True,
                )
            )
            .prefetch_related(
                Prefetch(
                    "class_subjects",
                    queryset=active_class_subjects,
                )
            )
            .order_by("section", "name")
        )

        return classes

    @classmethod
    def get_public_academic_sections(cls):

        classes = cls.get_public_classes()

        return {
            "nursery": [
                school_class
                for school_class in classes
                if school_class.section == "nursery"
            ],
            "primary": [
                school_class
                for school_class in classes
                if school_class.section == "primary"
            ],
        }

    @classmethod
    def get_public_class_detail(cls, slug):

        active_class_subjects = (
            ClassSubject.objects
            .filter(
                is_active=True,
                subject__is_active=True,
            )
            .select_related("subject")
        )

        return (
            SchoolClass.objects
            .prefetch_related(
                Prefetch(
                    "class_subjects",
                    queryset=active_class_subjects,
                )
            )
            .get(
                slug=slug,
            )
        )