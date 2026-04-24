from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение: владелец может редактировать/удалять, остальные только читать"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.customer == request.user


class IsOwner(permissions.BasePermission):
    """Только владелец"""

    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user