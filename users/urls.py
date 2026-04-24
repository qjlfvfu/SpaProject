from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # HTML представления
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),

    # API представления
    path('api/register/', views.APIRegistrationView.as_view(), name='api_register'),
    path('api/login/', views.APILoginView.as_view(), name='api_login'),
    path('api/profile/', views.APIProfileView.as_view(), name='api_profile'),
    path('api/telegram/', views.APITelegramConnectView.as_view(), name='api_telegram'),
]