from rest_framework.permissions import BasePermission

class IsGerente(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Gerentes').exists()