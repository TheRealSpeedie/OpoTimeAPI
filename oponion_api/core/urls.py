from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, MyTokenObtainPairView, ProjectsView, 
    TaskView, InvitationView, UserSearchView, UserInformationView, 
    MyTokenRefreshView, list_invitable_users, invite_user, confirm_invitation, 
    invited_users_with_status, MeetingView, reset_password, UserImageView,
    ShiftView, ProjectTimeEntryView, TaskTimeEntryView
)

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('register/', RegisterView.as_view()),
    path('login/', MyTokenObtainPairView.as_view()),
    path('projects/', ProjectsView.as_view()),
    path('task/', TaskView.as_view()),
    path('user-search/', UserSearchView.as_view()),
    path("users/selectable/", list_invitable_users, name="user-selectable"),
    path('invitation/', InvitationView.as_view()),
    path('refresh/', MyTokenRefreshView.as_view(), name="token_refresh"),
    path('info/', UserInformationView.as_view()),
    path('meeting/', MeetingView.as_view()),
    path("invitations/send/", invite_user, name="invite-user"),
    path("invitations/confirm/<uuid:token>/", confirm_invitation, name="confirm-invitation"),
    path("projects/<int:project_id>/invited-users/", invited_users_with_status),
    path("password/reset", reset_password),
    path('userImage/', UserImageView.as_view()),
    path('shifts/', ShiftView.as_view()),
    path('project-time/', ProjectTimeEntryView.as_view()),
    path('task-time/', TaskTimeEntryView.as_view()),
] 