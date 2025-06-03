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

# SHIFT
class Shift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shifts")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}: {self.start_time} - {self.end_time}"

# PROJECT TIME ENTRY
class ProjectTimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_time_entries")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="time_entries")
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name="project_entries")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.start_time} - {self.end_time})"

# TASK TIME ENTRY   
class TaskTimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="task_time_entries")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_entries")
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name="task_entries")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.task.text} ({self.start_time} - {self.end_time})"

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
    username = models.CharField(max_length=50)
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

# MEETING
class Meeting(models.Model):
    creator = models.ForeignKey(User, related_name='created_meetings', on_delete=models.CASCADE)
    invited_users = models.ManyToManyField(User, related_name='invited_meetings', blank=True)
    text = models.CharField(max_length=255)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()

    def __str__(self):
        return f"{self.text} ({self.from_date} - {self.to_date})"

# USERIMAGE
class UserImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images")
    image_data = models.BinaryField()  # Stores the actual image data
    content_type = models.CharField(max_length=100)  # To store the MIME type
    type = models.CharField(max_length=50, choices=[("profile", "Profile"), ("background", "Background")])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type}"
