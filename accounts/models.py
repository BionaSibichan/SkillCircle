
from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    full_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year_of_study = models.PositiveIntegerField()
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.full_name
