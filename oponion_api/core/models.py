from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import uuid

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

# TASK
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    
    text = models.CharField(max_length=255)
    description = models.TextField(blank=True) 

    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    PRIORITY_CHOICES = [
        ("high", "Hoch"),
        ("medium", "Mittel"),
        ("low", "Niedrig"),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")

    due_date = models.DateField(null=True, blank=True) 
    progress = models.PositiveIntegerField(default=0)  

    def __str__(self):
        return f"[{self.status} | {self.progress}%] {self.text} ({self.priority}) → {self.assigned_to.username}"

# TIME ENTRY
class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="entries")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="entries")
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
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.from_user} → {self.to_user} | {self.project.name} | {self.status}"

# USERINFORMATION
class UserInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    job = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    user_timezone = models.CharField(max_length=50, blank=True)
    languages = models.CharField(max_length=200, blank=True)  # z. B. "de,en,fr"
    bio = models.TextField(blank=True)
    joined_at = models.DateTimeField(default=timezone.now)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
