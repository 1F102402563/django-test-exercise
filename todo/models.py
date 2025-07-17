from django.db import models
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)

    PRIORITY_CHOICES = [
        (1, '1(重要)'),
        (2, '2'),
        (3, '3(まあまあ重要)'),
        (4, '4'),
        (5, '5(できれば)'),
    ]

    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt
