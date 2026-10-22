
from django.db import models
from django.contrib.auth.models import User
from exchanges.models import SkillExchange


class LearningSession(models.Model):
    exchange = models.ForeignKey(
        SkillExchange,
        on_delete=models.CASCADE,
        related_name='learning_sessions'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teaching_sessions'
    )
    learner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_sessions'
    )
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.teacher.username} - {self.session_date}"
