from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return request.user == obj and request.user.is_confirm

    def has_permission(self, request, view, **kwargs):
        if request.user.is_anonymous:
            return view.action == 'create'
        if request.user.is_superuser:
            return True
        if request.user.is_anonymous and view.action == 'create':
            return True
        if request.user.is_confirm and view.action == 'retrieve':
            return True
        return False
