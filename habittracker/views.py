from django.db import models
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from .models import Habit, Tracker
from .serializers import HabitSerializer, HabitListSerializer, TrackerSerializer
from .paginators import HabitPagination
from .permissions import IsOwner, IsOwnerOrReadOnlyForTracker
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import HabitForm, TrackerForm
from django.contrib import messages
from django.shortcuts import redirect


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
        # Для всех действий: свои привычки + публичные привычки других пользователей
        return Habit.objects.filter(
            models.Q(customer=user) | models.Q(is_public=True)
        ).distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return HabitListSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Отметить привычку как выполненную"""
        habit = self.get_object()

        # Проверяем, не отмечали ли уже сегодня
        today = timezone.now().date()
        exists_today = Tracker.objects.filter(
            habit=habit, user=request.user, completed_date=today
        ).exists()

        if exists_today:
            return Response(
                {"error": "Сегодня вы уже отмечали эту привычку"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Создаем отметку о выполнении
        tracker = Tracker.objects.create(
            habit=habit, user=request.user, status=True, completed_date=today
        )

        serializer = TrackerSerializer(tracker)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Статистика по привычке"""
        habit = self.get_object()
        trackers = habit.trackers.filter(user=request.user)

        total = trackers.count()
        completed = trackers.filter(status=True).count()
        success_rate = (completed / total * 100) if total > 0 else 0

        # Последние 7 дней
        last_week = []
        today = timezone.now().date()
        for i in range(7):
            day = today - timezone.timedelta(days=i)
            tracked = trackers.filter(completed_date=day, status=True).exists()
            last_week.append({"date": day.isoformat(), "completed": tracked})

        return Response(
            {
                "total_trackings": total,
                "completed": completed,
                "success_rate": round(success_rate, 2),
                "last_week": last_week,
            }
        )


class PublicHabitListView(viewsets.ReadOnlyModelViewSet):
    """Только публичные привычки (для всех пользователей)"""

    serializer_class = HabitListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["is_pleasant"]
    search_fields = ["name", "action"]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).select_related("customer")


class TrackerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyForTracker]
    """ViewSet для отметок выполнения"""

    serializer_class = TrackerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tracker.objects.filter(user=self.request.user).select_related("habit")

    def perform_create(self, serializer):
        # Проверяем, что привычка принадлежит пользователю
        habit = serializer.validated_data.get("habit")
        if habit.customer != self.request.user:
            raise ValidationError("Вы можете отмечать выполнение только своих привычек")

        # Проверяем, что дата не в будущем
        completed_date = serializer.validated_data.get(
            "completed_date", timezone.now().date()
        )
        if completed_date > timezone.now().date():
            raise ValidationError("Нельзя отметить выполнение в будущем")

        # Проверяем, нет ли уже отметки за этот день
        exists = Tracker.objects.filter(
            habit=habit, user=self.request.user, completed_date=completed_date
        ).exists()

        if exists:
            raise ValidationError(f"За {completed_date} вы уже отмечали эту привычку")

        serializer.save(user=self.request.user)


class HabitListView(LoginRequiredMixin, ListView):
    model = Habit
    template_name = "habits/habit_list.html"
    context_object_name = "object_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Habit.objects.filter(customer=self.request.user)
        status = self.request.GET.get("status")
        if status == "pleasant":
            queryset = queryset.filter(is_pleasant=True)
        elif status == "useful":
            queryset = queryset.filter(is_pleasant=False)
        elif status == "public":
            queryset = queryset.filter(is_public=True)
        return queryset


class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"
    success_url = reverse_lazy("habits:habit_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.customer = self.request.user
        messages.success(self.request, "Привычка успешно создана!")
        return super().form_valid(form)


class HabitDetailView(LoginRequiredMixin, DetailView):
    model = Habit
    template_name = "habits/habit_detail.html"

    def get_queryset(self):
        return Habit.objects.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trackers = Tracker.objects.filter(habit=self.object, user=self.request.user)
        context["success_count"] = trackers.filter(status=True).count()
        context["fail_count"] = trackers.filter(status=False).count()
        return context


class HabitUpdateView(LoginRequiredMixin, UpdateView):
    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"
    success_url = reverse_lazy("habits:habit_list")

    def get_queryset(self):
        return Habit.objects.filter(customer=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Привычка успешно обновлена!")
        return super().form_valid(form)


class HabitDeleteView(LoginRequiredMixin, DeleteView):
    model = Habit
    template_name = "habits/habit_confirm_delete.html"
    success_url = reverse_lazy("habits:habit_list")

    def get_queryset(self):
        return Habit.objects.filter(customer=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Привычка удалена!")
        return super().delete(request, *args, **kwargs)


def complete_habit(request, pk):
    import traceback
    from django.utils import timezone
    from .models import Habit, Tracker

    try:
        habit = Habit.objects.get(pk=pk, customer=request.user)
        Tracker.objects.create(
            habit=habit,
            user=request.user,
            status=True,
            completed_date=timezone.now().date()
        )
        messages.success(request, f'Привычка "{habit.name}" отмечена как выполненная!')
        return redirect("habits:habit_detail", pk=pk)
    except Exception as e:
        print("ОШИБКА:", e)
        traceback.print_exc()
        messages.error(request, f"Не удалось отметить привычку: {e}")
        return redirect("habits:habit_list")


class TrackerCreateView(LoginRequiredMixin, CreateView):
    model = Tracker
    form_class = TrackerForm
    template_name = "habits/tracker_form.html"
    success_url = reverse_lazy("habits:habit_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
