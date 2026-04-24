from django.db import models
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Habit, Tracker
from .serializers import HabitSerializer, HabitListSerializer, TrackerSerializer
from .paginators import HabitPagination
from .permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычек"""

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = HabitPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_pleasant", "is_public"]
    search_fields = ["name", "action"]
    ordering_fields = ["time", "period", "name"]
    ordering = ["time"]

    def get_queryset(self):
        user = self.request.user
        if self.action == "list":
            # Список: свои + публичные чужие
            return Habit.objects.filter(
                models.Q(customer=user) | models.Q(is_public=True)
            ).distinct()
        # Детальный просмотр: свои или публичные
        return Habit.objects.filter(models.Q(customer=user) | models.Q(is_public=True))

    def get_serializer_class(self):
        if self.action == "list":
            return HabitListSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class PublicHabitListView(viewsets.ReadOnlyModelViewSet):
    """Только публичные привычки (для всех пользователей)"""

    serializer_class = HabitListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)


class TrackerViewSet(viewsets.ModelViewSet):
    """ViewSet для отметок выполнения"""

    serializer_class = TrackerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tracker.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
