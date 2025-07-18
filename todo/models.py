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

    edit_at = models.DateTimeField(null=True, blank=True)
    

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    posted_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Comment on {self.task.title} by {self.posted_at.strftime('%Y-%m-%d %H:%M')}"

class ChecklistItem(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklist_items')
    text = models.CharField(max_length=200)  # テキスト
    is_checked = models.BooleanField(default=False)  # チェック状態
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.is_checked}: {self.text}"
