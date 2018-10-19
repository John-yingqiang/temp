from rest_framework import permissions
from ipaddress import ip_network, ip_address
import os


WHITE_NETS = os.environ.get('WHITE_NETS', '').split(',')


def ip_in_white_list(ip, nets):
    ip = ip_address(ip)
    return any((ip in n for n in nets))


class WhiteListOnly(permissions.BasePermission):

    nets = [ip_network(n) for n in WHITE_NETS]

    def _is_in_white_list(self, request):
        if request.method in permissions.SAFE_METHODS:
            return True
        ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
        return ip_in_white_list(ip, self.nets)

    def has_permission(self, request, view):
        return self._is_in_white_list(request) or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return self._is_in_white_list(request) or request.user.is_superuser


class IsCustomUser(permissions.BasePermission):
    """
    Allows write access only to admin users.
    """
    def has_permission(self, request, view):
        token = request.token_data
        user_id = token.get('user_id')
        return isinstance(user_id, int) or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
