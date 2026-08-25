from django.db import models


class AcademicYear(models.Model):

    name = models.CharField(
        max_length=20,
        unique=True
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name

class Term(models.Model):
    
    TERM_CHOICES = [
        ("first", "First Term"),
        ("second", "Second Term"),
        ("third", "Third Term"),
    ]

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="terms"
    )

    name = models.CharField(
        max_length=20,
        choices=TERM_CHOICES
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.academic_year} - {self.get_name_display()}"


class SchoolClass(models.Model):
    
    SECTION_CHOICES = [
        ("nursery", "Nursery"),
        ("primary", "Primary"),
    ]

    name = models.CharField(
        max_length=50
    )

    section = models.CharField(
        max_length=20,
        choices=SECTION_CHOICES
    )

    def __str__(self):
        return self.name

class Subject(models.Model):
    
    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


class ClassSubject(models.Model):

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="class_subjects",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="class_subjects",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "school_class",
                    "subject",
                ],
                name="unique_subject_per_class",
            ),

        ]

    def __str__(self):

        return (
            f"{self.school_class} - "
            f"{self.subject}"
        )