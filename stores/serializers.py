from rest_framework import serializers
from .models import *

# from configs.sign import verify_md5
from django.core.cache import cache


class CreditCoinConfigSerializer(serializers.ModelSerializer):
    event_action = serializers.JSONField(source='json_event')

    class Meta:
        model = CreditCoinConfig
        fields = ('name', 'uid', 'desc', 'icon', 'credit_coin_amount', 'is_continue', 'event_action', 'credit_coin_amount')


def get_credit_coin_config(reload=False):
    configs = None
    if not reload:
        configs = cache.get('coupons_CreditCoinConfig')

    if reload or not configs:
        coin_configs = CreditCoinConfig.objects.filter(is_active=True)
        ret_data = CreditCoinConfigSerializer(coin_configs, many=True).data
        configs = ret_data

        cache.set('coupons_CreditCoinConfig', ret_data)
    return configs


class CouponFilterSerializer(serializers.Serializer):

    is_hot = serializers.BooleanField(required=False)
    is_birthday = serializers.BooleanField(required=False)
    is_new_register = serializers.BooleanField(required=False)


class CouponNewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CouponNews
        fields = ('detail', 'event_action')


class CouponBannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = CouponBanner
        fields = ('image', 'event_action')


class CouponActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = CouponActivity
        fields = ('pic', 'event_action')


class CouponTypeSerializer(serializers.ModelSerializer):

    detail_list = serializers.ListField(source='json_detail')
    usage_list = serializers.ListField(source='json_usage')

    class Meta:
        model = CouponType
        fields = ('id', 'name', 'sub_name', 'level_min', 'credit_coin', 'icon', 'detail_list', 'event_action',
                  'usage_list', 'is_phone', 'is_phone_flow', 'phone_amount', 'is_credit_coin', 'credit_coin_amount',
                  'section', 'credit_coin', 'start_time', 'end_time', 'effective_days', 'is_new_register', 'is_birthday')


class CouponUseSerializer(serializers.Serializer):
    add_id = serializers.CharField()
    sign = serializers.CharField(required=False)

    def __init__(self, **kwargs):
        self.device = kwargs.pop('device', None)
        super(CouponUseSerializer, self).__init__(**kwargs)

    def validate(self, attrs):
        # verify_md5(attrs)
        # md5，包名，暂停md5签名，暂停话费充值功能
        return attrs
