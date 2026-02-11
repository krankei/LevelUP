from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):

    TASK_TYPES = [
        ('MAIN', 'Main Quest'),
        ('SIDE', 'Side Quest'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)

    task_type = models.CharField(
        max_length=10,
        choices=TASK_TYPES,
        default='MAIN'
    )

    time_slot = models.TimeField(blank=True, null=True)

    # 🔥 NEW
    duration_hours = models.IntegerField(default=1)
    xp_value = models.IntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.xp_value = self.duration_hours * 10
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.task_type})"


class WeeklyProgress(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'date')

    def __str__(self):
        return f"{self.task.title} - {self.date}"


# 🔥 NEW PROFILE MODEL
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def calculate_level(self):
        xp = self.total_xp
        level = 1
        required_xp = 500

        while xp >= required_xp:
            level += 1
            required_xp += 250

        self.level = level
        self.save()

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"
