from rest_framework import permissions

from accounts.models import User


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(not user.is_authenticated)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.role == User.ADMIN)


class IsProjectManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.role == User.PROJECT_MANAGER)


class IsDeveloper(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.role == User.DEVELOPER)
