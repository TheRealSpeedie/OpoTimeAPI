from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializer import MyTokenObtainPairSerializer, TaskSerializer, InvitationSerializer
from .models import Task, Project, Invitation
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

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
        return Response({"message": f"Hello {request.user.username}, your time entry endpoint works!"})

class ProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello {request.user.username}, your time entry endpoint works!"})

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

        if not task_id or not new_status:
            return Response({"error": "task_id and new status required"}, status=400)

        task = get_object_or_404(Task, id=task_id)
        task.status = new_status
        task.save()
        return Response({"message": f"Task status changed to {new_status}."})

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

        serializer = InvitationSerializer(data={
            "from_user": request.user.id,
            "to_user": to_user_id,
            "project": project_id,
            "status": "pending"
        })

        if serializer.is_valid():
            serializer.save()
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


