from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    # NEW
    is_weekly = models.BooleanField(default=False)
    time_slot = models.CharField(max_length=20, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

