from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm
from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    TelegramSetSerializer,
)
from .models import CustomUser
from .serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей (API)"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)


# ========== ШАБЛОННЫЕ ПРЕДСТАВЛЕНИЯ (для HTML) ==========


class UserRegisterView(CreateView):
    """Регистрация нового пользователя (HTML)"""

    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        messages.success(
            self.request, "Регистрация прошла успешно! Теперь вы можете войти."
        )
        return super().form_valid(form)


class UserLoginView(LoginView):
    """Вход в систему (HTML)"""

    template_name = "users/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("home")

    def form_valid(self, form):
        messages.success(self.request, f"Добро пожаловать, {form.get_user().email}!")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """Выход из системы (HTML)"""

    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Вы вышли из системы.")
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, DetailView):
    """Профиль пользователя (HTML)"""

    model = CustomUser
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля (HTML)"""

    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)


# ========== API ПРЕДСТАВЛЕНИЯ (JSON) ==========


class APIRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя (API)"""

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class APILoginView(generics.GenericAPIView):
    """Авторизация пользователя (API / JWT)"""

    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response({"error": "Неверные учетные данные"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": CustomUserSerializer(user).data,
            }
        )


class APIProfileView(generics.RetrieveUpdateAPIView):
    """Профиль пользователя (API)"""

    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class APITelegramConnectView(generics.GenericAPIView):
    """Привязка Telegram chat_id (API)"""

    serializer_class = TelegramSetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.telegram_chat_id = serializer.validated_data["telegram_chat_id"]
        user.save()

        return Response({"message": "Telegram привязан"})
