from rest_framework import permissions
from ipaddress import ip_network, ip_address
import os


WHITE_NETS = os.environ.get('WHITE_NETS')
WHITE_NETS = WHITE_NETS.split(',') if WHITE_NETS else []


def ip_in_white_list(ip, nets):
    ip = ip_address(ip)
    return any((ip in n for n in nets))


class WhiteListOnly(permissions.BasePermission):

    nets = [ip_network(n) for n in WHITE_NETS]

    def _is_in_white_list(self, request):
        ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
        return ip_in_white_list(ip, self.nets)

    def has_permission(self, request, view):
        return self._is_in_white_list(request) or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return self._is_in_white_list(request) or request.user.is_superuser
