from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

# PROJECT
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("paused", "Paused"), ("completed", "Completed")], default="active")
    progress = models.IntegerField(default=0)  # 0–100
    total_time = models.DurationField(default=timedelta)
    today_time = models.DurationField(default=timedelta)
    deadline = models.DateField(null=True, blank=True)
    invited_users = models.ManyToManyField(User, related_name="invited_projects", blank=True)
    color = models.CharField(max_length=7, default="#3B82F6")
    is_timer_running = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# TIME ENTRY
class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="entries")
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=[("start", "Start"), ("end", "End")])

    def __str__(self):
        return f"{self.user.username} - {self.project.name} - {self.type} at {self.timestamp}"

# INVITATION
class Invitation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_invitations")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="invitations")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.from_user} → {self.to_user} | {self.project.name} | {self.status}"

# TASK
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    text = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    def __str__(self):
        return f"[{self.status}] {self.text} → {self.assigned_to.username}"
