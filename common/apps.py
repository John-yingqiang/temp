from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'common'

    def ready(self):
        from .signals import model_pre_delete, model_saved
