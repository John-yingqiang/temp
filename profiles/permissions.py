from rest_framework import permissions


class IsCustomUser(permissions.BasePermission):
    """
    Allows write access only to admin users.
    """
    def has_permission(self, request, view):
        return isinstance(request.user_id, int)

    def has_object_permission(self, request, view, obj):
        return isinstance(request.user_id, int)


class IsStaffUser(permissions.BasePermission):
    """
    Allows write access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff


class IsSuperUser(permissions.BasePermission):
    """
    Allows write access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_superuser


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Allows write access only to admin users.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class IsSuperUserOrCustomReadOnly(permissions.BasePermission):
    """
    Allows write access only to admin users.
    """
    def has_permission(self, request, view):
        return (isinstance(request.user_id, int) and request.method in permissions.SAFE_METHODS) or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser
