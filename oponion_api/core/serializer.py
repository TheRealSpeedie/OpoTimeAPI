from rest_framework import serializers
from .models import Task, Invitation, Project, UserInformation, Meeting, UserImage, ProjectTimeEntry, TaskTimeEntry, Shift
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get("username")  
        password = attrs.get("password")

        user = User.objects.filter(email=identifier).first()
        if user is None:
            user = User.objects.filter(username=identifier).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError("No active account found with the given credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data = super().validate({"username": user.username, "password": password})
        data["id"] = user.id
        return data

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ['from_user', 'status', 'timestamp']


class ProjectSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['user']

    def get_tasks(self, project):
        total = Task.objects.filter(project=project).count()
        completed = Task.objects.filter(project=project, status='done').count()
        return {
            "total": total,
            "completed": completed
        }

class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInformation
        fields = '__all__'

class UserSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email"] 


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = '__all__'
        read_only_fields = ('user', 'uploaded_at')

class MeetingSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.id')
    invited_users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Meeting
        fields = ['id', 'creator', 'invited_users', 'text', 'from_date', 'to_date']

    def validate(self, data):
        if data['to_date'] <= data['from_date']:
            raise serializers.ValidationError("„bis“ muss nach „von“ liegen.")
        return data

    def create(self, validated_data):
        invited = validated_data.pop('invited_users', [])
        meeting = Meeting.objects.create(
            creator=self.context['request'].user,
            **validated_data
        )
        meeting.invited_users.set(invited)
        return meeting

class ProjectTimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTimeEntry
        fields = '__all__'
        read_only_fields = ['user']

class TaskTimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTimeEntry
        fields = '__all__'
        read_only_fields = ['user']

class ShiftSerializer(serializers.ModelSerializer):
    project_entries = ProjectTimeEntrySerializer(many=True, read_only=True)
    task_entries = TaskTimeEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Shift
        fields = ['id', 'user', 'start_time', 'end_time', 'project_entries', 'task_entries']
        read_only_fields = ['user']

    def validate(self, data):
        if 'end_time' in data and data['end_time'] is not None:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("End time must be after start time")
        return data


