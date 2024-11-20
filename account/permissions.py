from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    def has_permission(self, request, view):
        # SAFE_METHODS include GET, HEAD, and OPTIONS requests, which are read-only
        if request.method in SAFE_METHODS:
            return True
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

class IsAuthenticatedOrReadOnlyCustom(BasePermission):
    """
    Custom permission to only allow authenticated users to perform any action,
    but allow read-only access to unauthenticated users.
    """
    def has_permission(self, request, view):
        # Allow read-only access for unauthenticated users
        if request.method in SAFE_METHODS:
            return True
        # Allow full access for authenticated users
        return request.user and request.user.is_authenticated
