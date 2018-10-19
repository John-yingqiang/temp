from .model_cache import CachedModel
from django.db.models.signals import post_save, pre_delete, post_migrate
from django.core.cache import cache
from django.dispatch import receiver
from .model_cache import cache_key, clear_cache_sig


def model_pre_delete(sender, instance, **kwargs):
    instance.delete_cache()


def model_saved(sender, instance, created, **kwargs):
    instance.delete_cache()


for subclass in CachedModel.__subclasses__():
    post_save.connect(model_saved, subclass)
    pre_delete.connect(model_pre_delete, subclass)
    post_migrate.connect(model_saved, subclass)


@receiver(clear_cache_sig)
def clear_cache(sender, **kwargs):
    filter_key = cache_key(sender, kwargs['key'])
    cache.delete(filter_key)
