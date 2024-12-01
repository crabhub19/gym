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
class IsAdminOrPostOnly(BasePermission): 
    def has_permission(self, request, view): 
        # Allow access if the user is an admin 
        if request.user and request.user.is_staff: 
            return True 
        # Allow access if the request method is POST 
        if request.method == 'POST': 
            return True 
        # Deny access otherwise 
        return False