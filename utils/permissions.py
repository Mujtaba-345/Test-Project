from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotAuthenticated


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_type == "mod":
            return True
        elif not request.user.is_authenticated:
            raise NotAuthenticated
        else:
            raise PermissionDenied("You do not have permission to access this resource.")


class IsModeratorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.user.is_authenticated and request.user.user_type == "user" and request.method in (
                'GET', 'HEAD', 'OPTIONS'):
            return True

        # Allow full access to moderators
        return request.user.is_authenticated and request.user.user_type == "mod"
