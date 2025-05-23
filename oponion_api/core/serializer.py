from rest_framework import serializers
from .models import Task, Invitation, Project, TimeEntry
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User

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
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['user']

class TimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = '__all__'
        read_only_fields = ['user']


