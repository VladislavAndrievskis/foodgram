"""
Разрешения: только автор или админ может редактировать.
"""

from rest_framework import permissions


class IsAuthorOrAdminPermission(permissions.BasePermission):
    message = "Изменение и удаление доступно только автору или администратору."

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )
