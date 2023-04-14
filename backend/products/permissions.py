from rest_framework.permissions import BasePermission


class ImportPermission(BasePermission):

    def has_permission(self, request, view, **kwargs):
        if request.user.is_superuser:
            return True
        return False


class UserItemPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return request.user == obj.user
