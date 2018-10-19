from rest_framework import serializers
from utils.invite_code import InviteCode
from django.core.cache import cache
from .models import AuthConfig, FeedBack
from .user_info import UserInfoMongo


def get_user_base_info_data(user_id):
    # fields = ('id', 'number', 'nickname', 'avatar_url', 'province', 'city', 'express_address', 'gender', 'birthday')
    # read_only_fields = ('id', 'number', 'gender', 'birthday')
    user_info = UserInfoMongo(user_id)
    data_more = {
        'credit_level_data': user_info.credit_level_data,
        'credit_score': user_info.credit_score,
        'credit_amount': user_info.credit_amount,
        'credit_coin': user_info.credit_coin,
        'invite_code': user_info.invite_code,
        'has_shared_friends': user_info.has_shared_friends
    }

    data_more.update(user_info.profile)
    return data_more


def get_user_coin_data(user_id):
    # fields = ('id', 'number', 'nickname', 'avatar_url', 'has_signed', 'to_sign_coin', 'credit_coin', 'credit_level')
    user_info = UserInfoMongo(user_id)
    data_more = {
        'has_signed': user_info.has_signed,
        'to_sign_coin': user_info.to_sign_coin,
        'credit_coin': user_info.credit_coin,
        'credit_level': user_info.credit_level
    }
    data_more.update(user_info.profile)
    return data_more


class JieProfileSerializer(serializers.Serializer):
    emergency_contact = serializers.CharField(max_length=32)
    emergency_number = serializers.CharField(max_length=11, min_length=11)
    degree = serializers.CharField(max_length=16)
    marriage = serializers.CharField(max_length=16)


class FakeProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=40, required=False)
    identification = serializers.CharField(max_length=22, required=False)
    qq = serializers.CharField(max_length=16, required=False)
    job = serializers.CharField(max_length=20, required=False)
    credit_card = serializers.CharField(max_length=40, required=False)
    id_image = serializers.URLField(required=False)
    id_image_back = serializers.URLField(required=False)
    number = serializers.CharField(max_length=16, required=False)
    number_service_password = serializers.CharField(max_length=16, required=False)
    bank_card = serializers.CharField(max_length=40, required=False)
    bank_name = serializers.CharField(max_length=40, required=False)
    nickname = serializers.CharField(max_length=40, required=False)
    avatar_url = serializers.URLField(required=False)


class FeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeedBack
        fields = ('sort', 'content',)


class UserInfoSerializer(serializers.Serializer):
    identification = serializers.CharField(max_length=22)
    number = serializers.CharField(max_length=24)


class AuthSerializer(serializers.ModelSerializer):

    event_action = serializers.JSONField()

    class Meta:
        model = AuthConfig
        fields = ('type', 'name', 'image', 'desc', 'event_action', )


def get_auth_config(reload=False):

    auth_priority = None
    authx = None
    if not reload:
        auth_priority = cache.get('auth_priority')
        authx = cache.get('authx')

    if reload or not authx:
        auth_priority = {
            "priority_1": list(AuthConfig.objects.filter(level='m').values_list('type', flat=True)),
            "priority_2": list(AuthConfig.objects.filter(level='o').values_list('type', flat=True)),
        }
        auths = AuthConfig.objects.exclude(level='i')
        authx = AuthSerializer(auths, many=True).data

        cache.set('auth_priority', auth_priority)
        cache.set('authx', authx)
        print("authx_reloaded")

    return auth_priority, authx


class JuPeiSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    image_url = serializers.URLField()
