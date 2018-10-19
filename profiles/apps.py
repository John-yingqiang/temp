from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        from .signals import auth_changed
