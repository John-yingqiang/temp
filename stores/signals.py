from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import CreditCoinConfig
from .serializers import CreditCoinConfigSerializer, get_credit_coin_config


def coin_config_changed(sender, instance, *args, **kwargs):
    get_credit_coin_config(True)


post_save.connect(coin_config_changed, CreditCoinConfig)
post_delete.connect(coin_config_changed, CreditCoinConfig)
