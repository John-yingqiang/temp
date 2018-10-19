from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import FeedbackSerializer, FakeProfileSerializer, UserInfoSerializer, get_user_coin_data, \
    get_user_base_info_data, JieProfileSerializer, JuPeiSerializer
from .permissions import IsCustomUser, IsSuperUser, IsStaffUser
from utils.validators import RaiseMessage
from stores.models import CouponType, CouponTypeValidate
from stores.status import *
from common.renderers import MongoJsonEncoder
from common.permissions import WhiteListOnly
from common.mongo import mongodb
import json
# TODO(ChenQiushi): 印尼，待定
# from general.settings import IMPLICIT_USER
from general.settings import STATIC_URL
from general.events import UserEvent
from django.template.response import TemplateResponse
# from configs.serializers import get_auth_config
from general.settings import JIE_DOMAIN, API_ID_INFO, API_PHONE_INFO
from datetime import datetime
from .user_info import UserInfoMongo
from .serializers import get_auth_config
import requests
from .models import FeedBack, JuPei
from rest_framework.decorators import detail_route, list_route
from rest_framework.viewsets import ReadOnlyModelViewSet
import jieba
import re
from vendors.baidu_ocr import baidu_word_ocr
from common.logs import add_log_count
import traceback


class FeedbackView(APIView):

    permission_classes = (IsCustomUser,)

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = request.token_data
        number = token_data['number']
        device_id = token_data.get('device_id')
        serializer.save(number=number, device_id=device_id)
        return Response({'status': 1})


class ProfileView(APIView):

    permission_classes = (IsCustomUser,)

    def get(self, request):
        user_id = request.user_id
        return Response(get_user_base_info_data(user_id))

    def post(self, request):
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        try:  #身份认证相关 from_proj = 'jie'
            serializer = JieProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            user_info.update_profile(data, 'jie')
        except:  # user.from_proj = 'dai'， 兼容头像，昵称等场景
            data = request.data.copy()
            user_info.update_profile(data)
        return self.get(request)


# 单一产品 fake 信息
class FakeProfileView(APIView):
    permission_classes = (IsCustomUser,)

    def get(self, request):
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        return Response(user_info.fake_profile)

    def post(self, request):
        user_id = request.user_id
        serializer = FakeProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_info = UserInfoMongo(user_id)
        user_info.update_fake_profile(data)
        return self.get(request)


# 信用等级页面
class CreditLevelView(APIView):

    permission_classes = (IsCustomUser,)

    def get(self, request):
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        auth = user_info.auth
        auth_priority, authx = get_auth_config()
        if authx:
            for a in authx:
                a['auth'] = auth.get(a['type'], 0)
        ret = {
            'user': get_user_base_info_data(user_id),
            'auth_priority': auth_priority,
            'authx': authx
        }
        auth_identification = ret['user'].get('auth', {}).get('identification')
        if auth_identification == 1:
            ret['user']['auth']['identification'] = 10
        return Response(ret)


# 签到
class SignInView(APIView):
    permission_classes = (IsCustomUser,)

    def post(self, request):
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        if not user_info.has_signed:
            user_info.sign_in()
            ret = get_user_coin_data(user_id)
            return Response(ret)
        RaiseMessage().has_signed()


# 分享好友
class ShareFriendView(APIView):
    permission_classes = (IsCustomUser,)

    def post(self, request):
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        user_info.update_share_friends()
        return Response({})


def user_redbags_view(request):
    context = {'static': STATIC_URL}
    return TemplateResponse(request, 'redbags/index.html', context)


# 我的红包
class UserConponsView(APIView):
    permission_classes = (IsCustomUser,)

    def get(self, request):
        # 用户的券
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        ret = {}

        if user_info.is_birthday:
            ret['is_birthday'] = {
                "name": "生日特权大礼包",
                "icon": "https://platplat.oss-cn-shanghai.aliyuncs.com/coupons/icon/birthday_gift.png",
                'event_action': {
                    'link': JIE_DOMAIN + '/misc/stores/coins#/List/?data={"is_birthday":true}&name=生日特权'
                }
            }

        if user_info.is_new_register:
            ret['is_new_register'] = {
                "name": "新人专享大礼包",
                "icon": "https://platplat.oss-cn-shanghai.aliyuncs.com/coupons/icon/new_register.png",
                'event_action': {
                    'link': JIE_DOMAIN + '/misc/stores/coins#/List/?data={"is_new_register":true}&name=新人专享'
                }
            }

        ret['coins_url'] = JIE_DOMAIN + '/misc/stores/coins'

        coupons = user_info.coupons
        validate_coupons = []
        for user_coupon in coupons:
            coupon = user_coupon['coupon']
            validate = CouponTypeValidate(coupon)
            add_id = user_coupon['add_id']
            data_ret = {}

            # 失效时间
            check_coupon_time = validate.check_coupon_time(user_info, user_coupon['user_created'])
            if check_coupon_time['expire'] or user_coupon['use_status'] == USED:
                user_info.delete_coupon(add_id)  # 删除过期券、使用成功券
                continue

            time_effective = check_coupon_time['time_effective'] or '~'
            time_expire = check_coupon_time['time_expire'] or '~'

            bottom_tip = []
            if check_coupon_time['time_effective']:
                bottom_tip.append('开始时间：%s' % time_effective.strftime('%Y-%m-%d %H:%M:%S'))
            if check_coupon_time['time_expire']:
                bottom_tip.append('截止时间：%s' % time_expire.strftime('%Y-%m-%d %H:%M:%S'))
            elif coupon['is_birthday']:
                bottom_tip = bottom_tip.append('生日特权')
            elif coupon['is_new_register']:
                bottom_tip = bottom_tip.append('新人专享')
            else:
                bottom_tip = bottom_tip.append('信用权益')

            # 底部 tip
            data_ret['bottom_tip'] = bottom_tip

            # button
            check_can_use = validate.check_can_use(user_info, user_coupon['user_created'], user_coupon['use_status'])
            data_ret['effective'] = check_can_use['enable']
            data_ret['button_text'] = check_can_use['tip']

            # 面值f
            if coupon['is_credit_coin']:  # 奖励信用币
                show_num = coupon['credit_coin_amount']
                show_unit = '个'
            else:
                show_num = coupon['phone_amount']/100.0
                show_unit = '元'
            data_ret['show_num'] = show_num
            data_ret['show_unit'] = show_unit
            # 红包 UI
            coupon_ret = {
                'name': coupon['name'],
                'icon': coupon['icon']
            }
            data_ret['coupon'] = coupon_ret
            data_ret['add_id'] = user_coupon['add_id']

            validate_coupons.append(data_ret)

        ret['coupons'] = json.loads(MongoJsonEncoder().encode(validate_coupons))
        return Response(ret)


# 删除统计渠道用户接口，改从 es 获取


class IdInfoView(APIView):
    # permission_classes = (IsCustomUser,)

    def post(self, request):
        serializer = UserInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ret = {}
        # 内网获取身份证信息
        # url_id = MARKET_HOST + '/mobile/idinfo'
        id_info = {}
        try:
            url_id = API_ID_INFO.format(data['identification'])
            r_id = requests.get(url_id, timeout=5)
            id_info = r_id.json()
        except:
            pass

        if id_info:
            ret.update(id_info)

        # 内网获取手机运营商
        # url_number = MARKET_HOST + '/mobile/info/' + data['number']
        url_number = API_PHONE_INFO.format(data['number'])
        number_info = {}
        try:
            r_number = requests.get(url_number, timeout=5)
            number_info = r_number.json()
        except:
            pass

        if number_info:
            ret.update({'phone_type': number_info.get('phone_type')})

        ret['apply_time'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        return Response(ret)


class JuPeiViewSet(ReadOnlyModelViewSet):
    permission_classes = (WhiteListOnly,)
    queryset = JuPei.objects
    serializer_class = FeedbackSerializer

    def _check_ocr_words(self, tags):
        """
        取出mongodb中排序靠前的1000个，计算tags中占比
        :param tags:
        :return:
        """
        return len(tags)

    @list_route(methods=['post'], permission_classes=(IsCustomUser,), url_name='apply')
    def apply(self, request):
        serializer = JuPeiSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        image_url = data['image_url']
        product_id = data['product_id']
        token = request.token_data
        ju, created = JuPei.objects.update_or_create(user_id=token['user_id'], defaults={'number': token['number']})

        try:
            success, words = baidu_word_ocr(image_url)
        except:
            add_log_count('baidu_word_ocr')
            traceback.print_exc()
            success, words = None, None

        if success:
            if words:  # ocr接口调用成功且有文字，通过；ocr接口调用失败也通过
                tags = list(jieba.cut(re.sub(r'[^\u4e00-\u9fa5]', '', words)))
                if tags and self._check_ocr_words(tags):
                    bulk = mongodb.jupei_words.initialize_ordered_bulk_op()
                    for tag in tags:
                        bulk.find({'_id': tag}).upsert().update({'$inc': {'word_count': 1}})
                    bulk.execute()
                else:
                    return Response({'amount_add': 0, 'review': '未通过审核'})
            else:
                return Response({'amount_add': 0, 'review': '未通过审核'})

        amount_add, msg = ju.update_pei(product_id)
        return Response({'amount_add': amount_add, 'review': msg})

    @list_route(methods=['get'], permission_classes=(IsStaffUser,), url_name='words')
    def wordocr(self, request):
        words = mongodb.jupei_words.find(sort=[('word_count', -1)])
        return Response(list(words)[:1000])

    def retrieve(self, request, *args, **kwargs):
        user_id = int(kwargs['pk'])
        instance, created = JuPei.objects.get_or_create(user_id=user_id)
        users = mongodb.users.find_one({'_id': user_id}) or {}
        ret = {
            'amount': instance.amount,
            'send_count': instance.send_count,
            'withdraw': 0,  # 提现金额目前只能为0
            'jupei_applied': users.get('jupei_applied', [])
        }
        return Response(ret)
