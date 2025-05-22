from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, TimeEntryView, MyTokenObtainPairView, ProjectsView, TaskView, InvitationView, UserSearchView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('register/', RegisterView.as_view()),
    path('login/', MyTokenObtainPairView.as_view()),
    path('projects/', ProjectsView.as_view()),
    path('task/', TaskView.as_view()),
    path('user-search/', UserSearchView.as_view()),
    path('invitation/', InvitationView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('time/', TimeEntryView.as_view()),
]