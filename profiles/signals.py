from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import AuthConfig
from .serializers import AuthSerializer, get_auth_config


def auth_changed(sender, instance, *args, **kwargs):
    print('auth_changed')
    get_auth_config(True)


post_save.connect(auth_changed, AuthConfig)
post_delete.connect(auth_changed, AuthConfig)
