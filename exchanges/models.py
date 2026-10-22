
from django.db import models
from django.contrib.auth.models import User
from skills.models import Skill


class SkillExchange(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_exchanges'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_exchanges'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.username} - {self.skill.skill_name}"
