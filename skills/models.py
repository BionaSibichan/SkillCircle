
from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('creative', 'Creative'),
        ('communication', 'Communication'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    skill_name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField(blank=True)
    is_offered = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.skill_name
