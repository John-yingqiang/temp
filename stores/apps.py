from django.apps import AppConfig


class CouponsConfig(AppConfig):
    name = 'stores'

    def ready(self):
        from .signals import coin_config_changed
