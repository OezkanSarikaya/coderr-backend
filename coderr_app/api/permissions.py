from rest_framework.permissions import BasePermission, SAFE_METHODS
import logging
logger = logging.getLogger(__name__)

class IsAuthenticatedOrReadOnlyForProfile(BasePermission):
    """
    Allows read access for everyone, write access only for authenticated users,
    who have the profile.
    """
    def has_permission(self, request, view):
        # Read access (GET, HEAD, OPTIONS) is permitted for all
        if request.method in SAFE_METHODS:
            return True
        # Write access is only permitted for authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read access to the object is permitted for everyone
        if request.method in SAFE_METHODS:
            return True
        is_owner = obj.user == request.user
        logger.debug(f"User: {request.user}, Is Owner: {is_owner}")
        return is_owner
        
        

class IsBusinessUserOrReadOnly(BasePermission):
    """
    Allows GET and other ‘secure’ methods for all users.
    POST and other write methods are only allowed for ‘business’ users.
    """

    def has_permission(self, request, view):
        # Allow ‘secure’ methods (GET, HEAD, OPTIONS) for all users
        if request.method in SAFE_METHODS:
            return True

        # For write methods, check whether the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check whether the user is of the ‘business’ type
        return getattr(request.user.profile, 'type', None) == 'business'


class IsReviewerOrAdmin(BasePermission):
    """
    Update or delete olny for owner or admin allowed
    """

    def has_object_permission(self, request, view, obj):
        # Read allowed for everone
        if request.method in SAFE_METHODS:
            return True

        # check if user ist owner of review or admin
        return request.user == obj.reviewer or request.user.is_staff
    
class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission: Only the owner of an object can edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS (GET, HEAD, OPTIONS) allowed for veryone
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # For PUT, PATCH und DELETE the user hast to be the owwner
        return obj.user == request.user
