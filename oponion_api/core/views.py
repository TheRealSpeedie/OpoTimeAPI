from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializer import MyTokenObtainPairSerializer, TaskSerializer, InvitationSerializer, ProjectSerializer, UserInformationSerializer, UserSelectSerializer, MeetingSerializer, UserImageSerializer, ShiftSerializer, ProjectTimeEntrySerializer, TaskTimeEntrySerializer
from .models import Task, Project, Invitation, UserInformation, Meeting, UserImage, Shift, ProjectTimeEntry, TaskTimeEntry

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import datetime, timezone
from django.utils import timezone
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from .utils import send_invitation_email

from django.utils import timezone
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import send_invitation_email

import base64



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

        UserInformation.objects.create(
            email = email,
            user=user,
            first_name=request.data.get("first_name", ""),
            last_name=request.data.get("last_name", ""),
            phone=request.data.get("phone", ""),
            job=request.data.get("job", ""),
            location=request.data.get("location", ""),
            user_timezone=request.data.get("timezone", ""),
            languages=request.data.get("languages", ""),
            bio=request.data.get("bio", ""),
            joined_at=timezone.now()
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "User created successfully.",
            "id": user.id,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=201)


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

        projects = Project.objects.filter(creator=request.user) | request.user.invited_projects.all()
        serializer = ProjectSerializer(projects.distinct(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        project_id = request.data.get("project_id")
        project = get_object_or_404(Project, id=project_id, creator=request.user)

        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request):
        project_id = request.query_params.get("project_id")
        project = get_object_or_404(Project, id=project_id, creator=request.user)
        project.delete()
        return Response({"message": "Project deleted successfully."}, status=204)

class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        task_id = request.query_params.get("task_id")
        priority = request.query_params.get("priority")

        if task_id:
            task = get_object_or_404(Task, id=task_id)
            serializer = TaskSerializer(task)
            return Response(serializer.data)

        if priority:
            tasks = Task.objects.filter(priority=priority)
        elif project_id:
            tasks = Task.objects.filter(project__id=project_id)
        else:
            tasks = Task.objects.all()

        tasks = tasks.filter(assigned_to=request.user) 
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

        invitations = invitations.filter(from_user=request.user) 
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)

    def post(self, request):
        project_id = request.data.get("project_id")
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
        user_id = request.query_params.get("user_ID")

        if not query and not user_id:
            return Response({"error": "Query parameter 'q' or 'user_ID' is required"}, status=400)

        users = User.objects.none()

        if query:
            users = User.objects.filter(
                username__icontains=query
            ) | User.objects.filter(
                email__icontains=query
            )

        if user_id:
            users = users | User.objects.filter(id=user_id)

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

class UserInformationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            user_info = request.user.info 
            serializer = UserInformationSerializer(user_info)
            return Response(serializer.data)
        except UserInformation.DoesNotExist:
            return Response({"error": "User information not found."}, status=404)

    def put(self, request):
        try:
            user_info = request.user.info
            serializer = UserInformationSerializer(user_info, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except UserInformation.DoesNotExist:
            return Response({"error": "User information not found."}, status=404)

    def patch(self, request):
        try:
            user_info = request.user.info
            serializer = UserInformationSerializer(user_info, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except UserInformation.DoesNotExist:
            return Response({"error": "User information not found."}, status=404)

class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=400)

            token = RefreshToken(refresh_token)
            data = {
                'access': str(token.access_token),
                'refresh': str(token)
            }
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=401)

class MeetingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meeting_id = request.query_params.get("meeting_id")

        if meeting_id:
            meeting = get_object_or_404(Meeting, id=meeting_id)
            if meeting.creator != request.user and request.user not in meeting.invited_users.all():
                return Response({"error": "Not authorized to view this meeting."}, status=403)
            serializer = MeetingSerializer(meeting)
            return Response(serializer.data)

        meetings = Meeting.objects.filter(
            models.Q(creator=request.user) | models.Q(invited_users=request.user)
        ).distinct()

        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MeetingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        meeting_id = request.data.get("meeting_id")
        if not meeting_id:
            return Response({"error": "meeting_id required"}, status=400)

        meeting = get_object_or_404(Meeting, id=meeting_id)
        if meeting.creator != request.user:
            return Response({"error": "Only the creator can edit this meeting."}, status=403)

        serializer = MeetingSerializer(meeting, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Meeting updated successfully."})
        return Response(serializer.errors, status=400)

    def delete(self, request):
        meeting_id = request.query_params.get("meeting_id")
        if not meeting_id:
            return Response({"error": "meeting_id required"}, status=400)

        meeting = get_object_or_404(Meeting, id=meeting_id)
        if meeting.creator != request.user:
            return Response({"error": "Only the creator can delete this meeting."}, status=403)

        meeting.delete()
        return Response({"message": "Meeting deleted successfully."}, status=204)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_invitable_users(request):
    users = User.objects.exclude(id=request.user.id)
    serializer = UserSelectSerializer(users, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_user(request):
    to_user_id = request.data.get("to_user_id")
    project_id = request.data.get("project_id")

    if not to_user_id or not project_id:
        return Response({"error": "Fehlende Daten"}, status=400)

    User = get_user_model()
    try:
        to_user = User.objects.get(id=to_user_id)
        project = Project.objects.get(id=project_id)
    except User.DoesNotExist:
        return Response({"error": "Benutzer nicht gefunden"}, status=404)
    except Project.DoesNotExist:
        return Response({"error": "Projekt nicht gefunden"}, status=404)

    invitation = Invitation.objects.create(
        from_user=request.user,
        to_user=to_user,
        project=project
    )

    send_invitation_email(invitation)

    return Response({"message": "Einladung gesendet"})

@api_view(["GET"])
def confirm_invitation(request, token):
    try:
        invitation = Invitation.objects.get(token=token, status='pending')
        invitation.status = "accepted"
        invitation.save()

        invitation.project.invited_users.add(invitation.to_user)

        return Response({"message": "Einladung erfolgreich bestätigt."})
    except Invitation.DoesNotExist:
        return Response({"error": "Ungültiger oder abgelaufener Einladungstoken."}, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invited_users_with_status(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Projekt nicht gefunden."}, status=404)

    invited_users = project.invited_users.all()

    result = []
    for user in invited_users:
        try:
            invitation = Invitation.objects.get(project=project, to_user=user)
            status = invitation.status
        except Invitation.DoesNotExist:
            status = "unbekannt"

        result.append({
            "id": user.id,
            "email": user.email,
            "name": user.username,
            "invitation_status": status
        })

    return Response(result)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_password(request):
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response({"error": "old_password und new_password sind erforderlich."}, status=400)

    user = request.user
    if not user.check_password(old_password):
        return Response({"error": "Das alte Passwort ist falsch."}, status=403)

    user.set_password(new_password)
    user.save()
    return Response({"message": "Passwort wurde erfolgreich geändert."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def infoForDisplay(request):
    userID = request.query_params.get("userID")

    if not userID:
        return Response({"error": "userID sind erforderlich."}, status=400)

    user = get_object_or_404(User, id=userID)
    
    profile_image = UserImage.objects.filter(user=user, type="profile").last()
    image_data = None
    
    if profile_image:
        base64_image = base64.b64encode(profile_image.image_data).decode('utf-8')
        image_data = f"data:{profile_image.content_type};base64,{base64_image}"

    response_data = {
        "email": user.email,
        "username": user.username,
        "profile_image": image_data
    }

    return Response(response_data)

class UserImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        image_type = request.query_params.get("type")  # e.g. profile, background
        if image_type:
            image = UserImage.objects.filter(user=request.user, type=image_type).last()
            if not image:
                return Response({"error": "Image not found"}, status=404)
            
            # Return base64 encoded image for the frontend
            base64_image = base64.b64encode(image.image_data).decode('utf-8')
            return Response({
                "image": f"data:{image.content_type};base64,{base64_image}",
                "type": image.type,
                "uploaded_at": image.uploaded_at
            })

        images = UserImage.objects.filter(user=request.user)
        image_data = []
        for image in images:
            base64_image = base64.b64encode(image.image_data).decode('utf-8')
            image_data.append({
                "image": f"data:{image.content_type};base64,{base64_image}",
                "type": image.type,
                "uploaded_at": image.uploaded_at
            })
        return Response(image_data)

    def post(self, request):
        file = request.FILES.get("file")
        image_type = request.data.get("type")

        if not file or not image_type:
            return Response({"error": "file and type are required"}, status=400)

        # Read the binary data from the uploaded file
        image_data = file.read()
        content_type = file.content_type

        # Save the image to the database
        image = UserImage.objects.create(
            user=request.user,
            image_data=image_data,
            content_type=content_type,
            type=image_type
        )

        # Return base64 encoded image for immediate use in frontend
        base64_image = base64.b64encode(image_data).decode('utf-8')
        return Response({
            "image": f"data:{content_type};base64,{base64_image}",
            "type": image.type,
            "uploaded_at": image.uploaded_at
        }, status=201)

    def patch(self, request):
        image_type = request.data.get("type")
        if not image_type:
            return Response({"error": "type required"}, status=400)

        image = UserImage.objects.filter(user=request.user, type=image_type).last()
        if not image:
            return Response({"error": "Image not found"}, status=404)
            
        image.type = image_type
        image.save()
        return Response({"message": "Image updated successfully"})

    def delete(self, request):
        image_type = request.query_params.get("type")
        if not image_type:
            return Response({"error": "type required"}, status=400)

        image = UserImage.objects.filter(user=request.user, type=image_type).last()
        if not image:
            return Response({"error": "Image not found"}, status=404)

        image.delete()
        return Response({"message": "Image deleted successfully."}, status=204)

class ShiftView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shift_id = request.query_params.get('shift_id')
        of_day = request.query_params.get('of_day')

        if shift_id:
            shift = get_object_or_404(Shift, id=shift_id, user=request.user)
            serializer = ShiftSerializer(shift)
            return Response(serializer.data)

        if of_day:
            shifts = Shift.objects.filter(user=request.user, start_time__date=of_day)
            serializer = ShiftSerializer(shifts, many=True)
            return Response(serializer.data)
        
        shifts = Shift.objects.filter(user=request.user)
        serializer = ShiftSerializer(shifts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShiftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request):
        shift_id = request.data.get('shift_id')
        shift = get_object_or_404(Shift, id=shift_id, user=request.user)
        
        serializer = ShiftSerializer(shift, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        shift_id = request.data.get('shift_id')
        shift = get_object_or_404(Shift, id=shift_id, user=request.user)
        
        serializer = ShiftSerializer(shift, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        shift_id = request.query_params.get('shift_id')
        shift = get_object_or_404(Shift, id=shift_id, user=request.user)
        shift.delete()
        return Response(status=204)

class ProjectTimeEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entry_id = request.query_params.get('entry_id')
        project_id = request.query_params.get('project_id')
        shift_id = request.query_params.get('shift_id')
        
        if entry_id:
            entry = get_object_or_404(ProjectTimeEntry, id=entry_id, user=request.user)
            serializer = ProjectTimeEntrySerializer(entry)
            return Response(serializer.data)
        
        entries = ProjectTimeEntry.objects.filter(user=request.user)
        
        if project_id:
            entries = entries.filter(project_id=project_id)
        if shift_id:
            entries = entries.filter(shift_id=shift_id)
            
        serializer = ProjectTimeEntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectTimeEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request):
        entry_id = request.data.get('entry_id')
        entry = get_object_or_404(ProjectTimeEntry, id=entry_id, user=request.user)
        
        serializer = ProjectTimeEntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        entry_id = request.data.get('entry_id')
        entry = get_object_or_404(ProjectTimeEntry, id=entry_id, user=request.user)
        
        serializer = ProjectTimeEntrySerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        entry_id = request.query_params.get('entry_id')
        entry = get_object_or_404(ProjectTimeEntry, id=entry_id, user=request.user)
        entry.delete()
        return Response(status=204)

class TaskTimeEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entry_id = request.query_params.get('entry_id')
        task_id = request.query_params.get('task_id')
        shift_id = request.query_params.get('shift_id')
        
        if entry_id:
            entry = get_object_or_404(TaskTimeEntry, id=entry_id, user=request.user)
            serializer = TaskTimeEntrySerializer(entry)
            return Response(serializer.data)
        
        entries = TaskTimeEntry.objects.filter(user=request.user)
        
        if task_id:
            entries = entries.filter(task_id=task_id)
        if shift_id:
            entries = entries.filter(shift_id=shift_id)
            
        serializer = TaskTimeEntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskTimeEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request):
        entry_id = request.data.get('entry_id')
        entry = get_object_or_404(TaskTimeEntry, id=entry_id, user=request.user)
        
        serializer = TaskTimeEntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        entry_id = request.data.get('entry_id')
        entry = get_object_or_404(TaskTimeEntry, id=entry_id, user=request.user)
        
        serializer = TaskTimeEntrySerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        entry_id = request.query_params.get('entry_id')
        entry = get_object_or_404(TaskTimeEntry, id=entry_id, user=request.user)
        entry.delete()
        return Response(status=204)


