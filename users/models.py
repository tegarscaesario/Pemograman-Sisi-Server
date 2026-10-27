from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        LECTURER = "LECTURER", "Dosen"
        STUDENT = "STUDENT", "Mahasiswa"
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    def __str__(self):
        return f"{self.username} ({self.role})"
