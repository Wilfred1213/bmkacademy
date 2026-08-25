from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("teacher", "Teacher"),
        ("parent", "Parent"),
        ("student", "Student"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="parent",
    )
    must_change_password = models.BooleanField(
        default=False
    )

class ParentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_profile"
    )

    phone = models.CharField(
        max_length=20
    )

    address = models.TextField(
        blank=True
    )

    occupation = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.user.get_full_name()