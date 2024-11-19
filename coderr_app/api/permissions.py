from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBusinessUserOrReadOnly(BasePermission):
    """
    Erlaubt GET und andere "sichere" Methoden für alle Benutzer.
    POST und andere schreibende Methoden sind nur für 'business'-Benutzer erlaubt.
    """
    def has_permission(self, request, view):
        # Erlaube "sichere" Methoden (GET, HEAD, OPTIONS) für alle Benutzer
        if request.method in SAFE_METHODS:
            return True

        # Für schreibende Methoden prüfen, ob der Benutzer authentifiziert ist
        if not request.user or not request.user.is_authenticated:
            return False

        # Überprüfen, ob der Benutzer vom Typ 'business' ist        
        return getattr(request.user.profile, 'type', None) == 'business'
    
from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework.permissions import BasePermission

class OrderPermissions(BasePermission):
    """
    Custom permission for OrderViewSet:
    - PATCH: Nur der `business_user` kann den Status von "in_progress" zu "completed" oder "cancelled" ändern.
    - PUT: Nicht erlaubt.
    - DELETE: Nur Admin-Benutzer (Staff).
    """

    def has_permission(self, request, view):
        # PUT ist für alle verboten
        if request.method == 'PUT':
            return False

        # DELETE ist nur für Admin-Benutzer erlaubt
        if request.method == 'DELETE':
            return request.user.is_staff

        # PATCH und andere Methoden werden in has_object_permission behandelt
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # PATCH: Business-User kann den Status ändern, wenn er "business_user" der Bestellung ist
        if request.method == 'PATCH':
            if request.user == obj.business_user:
                # Erlaubt nur, wenn der Status von "in_progress" auf "completed" oder "cancelled" geändert wird
                new_status = request.data.get('status')
                allowed_status_transitions = ["completed", "cancelled"]
                return obj.status == "in_progress" and new_status in allowed_status_transitions
            return False

        # DELETE: Nur Admin-Benutzer (überprüft bereits in has_permission)
        if request.method == 'DELETE':
            return request.user.is_staff

        # Standardmäßig erlauben, falls keine spezifische Regel greift
        return True
