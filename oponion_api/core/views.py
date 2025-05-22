from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializer import MyTokenObtainPairSerializer, TaskSerializer, InvitationSerializer, ProjectSerializer, TimeEntrySerializer
from .models import Task, Project, Invitation, TimeEntry
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from datetime import datetime, timezone


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "Username, email and password required."}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({"message": "User created successfully."}, status=201)

class TimeEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        user_id = request.query_params.get("user_id")
        since = request.query_params.get("since")

        if not since:
            return Response({"error": "since (ISO datetime) is required"}, status=400)

        if since.endswith("Z"):
            since = since.replace("Z", "+00:00")

        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            entries = TimeEntry.objects.filter(timestamp__gte=since_dt)

        entries = TimeEntry.objects.filter(timestamp__gte=since_dt)

        if project_id:
            entries = entries.filter(project__id=project_id)

        if user_id:
            entries = entries.filter(user__id=user_id)
        else:
            entries = entries.filter(user=request.user)

        serializer = TimeEntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TimeEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        entry_id = request.data.get("entry_id")
        entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user)

        serializer = TimeEntrySerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        entry_id = request.query_params.get("entry_id")
        entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
        entry.delete()
        return Response({"message": "Time entry deleted."}, status=204)

class ProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        project_name = request.query_params.get("project_name")

        if project_id:
            project = get_object_or_404(Project, id=project_id)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)

        if project_name:
            project = get_object_or_404(Project, name=project_name)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)

        projects = Project.objects.filter(user=request.user) | request.user.invited_projects.all()
        serializer = ProjectSerializer(projects.distinct(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        project_id = request.data.get("project_id")
        project = get_object_or_404(Project, id=project_id, user=request.user)

        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request):
        project_id = request.query_params.get("project_id")
        project = get_object_or_404(Project, id=project_id, user=request.user)
        project.delete()
        return Response({"message": "Project deleted successfully."}, status=204)

class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        task_id = request.query_params.get("task_id")

        if task_id:
            task = get_object_or_404(Task, id=task_id)
            serializer = TaskSerializer(task)
            return Response(serializer.data)

        if project_id:
            tasks = Task.objects.filter(project__id=project_id)
        else:
            tasks = Task.objects.all()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response({"error": "task_id required"}, status=400)
        
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return Response({"message": "Task deleted successfully."}, status=204)

    def patch(self, request):
        task_id = request.data.get("task_id")
        new_status = request.data.get("status")
        task_text = request.data.get("text")

        if not task_id or not new_status:
            return Response({"error": "task_id and new status required. The Attribut text is optional"}, status=400)

        task = get_object_or_404(Task, id=task_id)
        task.status = new_status

        if task_text:
            task.text = task_text

        task.save()
        return Response({"message": f"Task was successfully updated"})

class InvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        accepted_only = request.query_params.get("accepted") == "true"

        if not project_id:
            return Response({"error": "project_id is required"}, status=400)

        invitations = Invitation.objects.filter(project__id=project_id)

        if accepted_only:
            invitations = invitations.filter(status="accepted")

        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)

    def post(self, request):
        project_id = request.data.get("project")
        to_user_id = request.data.get("to_user")

        if not project_id or not to_user_id:
            return Response({"error": "project and to_user are required"}, status=400)

        data = {
            "to_user": to_user_id,
            "project": project_id,
            "status": "pending"
        }

        serializer = InvitationSerializer(data=data)

        if serializer.is_valid():
            serializer.save(from_user=request.user) 
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def patch(self, request):
        invitation_id = request.data.get("invitation_id")
        new_status = request.data.get("status")

        if not invitation_id or new_status not in ["pending", "accepted", "declined"]:
            return Response({"error": "Valid invitation_id and status required"}, status=400)

        invitation = get_object_or_404(Invitation, id=invitation_id)
        invitation.status = new_status
        invitation.save()

        return Response({"message": f"Invitation updated to {new_status}"})

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q")
        if not query:
            return Response({"error": "Query parameter 'q' is required"}, status=400)

        users = User.objects.filter(
            username__icontains=query
        ) | User.objects.filter(
            email__icontains=query
        )

        users = users.distinct()

        data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
            for user in users
        ]
        return Response(data)

