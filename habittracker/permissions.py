from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение: владелец может редактировать/удалять, остальные только читать"""

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для публичных привычек можно добавить проверку
        if hasattr(obj, "is_public") and obj.is_public and request.method == "GET":
            return True

        return obj.customer == request.user


class IsOwner(permissions.BasePermission):
    """Только владелец может выполнять любые действия"""

    def has_object_permission(self, request, view, obj):
        # Проверка на существование атрибута customer
        if not hasattr(obj, "customer"):
            return False
        return obj.customer == request.user


class IsOwnerOrReadOnlyForTracker(permissions.BasePermission):
    """Для трекера: пользователь может редактировать только свои записи"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class CanCompleteHabit(permissions.BasePermission):
    """Разрешение: пользователь может отметить выполнение только своих привычек"""

    def has_permission(self, request, view):
        # Для экшена complete проверяем владельца привычки
        if view.action == "complete" and view.kwargs.get("pk"):
            from .models import Habit

            try:
                habit = Habit.objects.get(pk=view.kwargs["pk"])
                return habit.customer == request.user
            except Habit.DoesNotExist:
                return False
        return True


class IsOwnerOrPublic(permissions.BasePermission):
    """Разрешение: владелец может всё, остальные только видят публичные привычки"""

    def has_object_permission(self, request, view, obj):
        # Публичные привычки могут читать все
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True
        # Остальные действия только для владельца
        return obj.customer == request.user
