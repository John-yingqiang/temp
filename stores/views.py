from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CouponTypeSerializer, CouponFilterSerializer, CouponBannerSerializer, CouponNewsSerializer, \
    CouponActivitySerializer, CouponUseSerializer, CreditCoinConfigSerializer, get_credit_coin_config
from utils.validators import RaiseMessage
from profiles.permissions import IsCustomUser, IsSuperUser, IsSuperUserOrCustomReadOnly
from profiles.serializers import get_user_coin_data, get_user_base_info_data
from rest_framework.viewsets import ReadOnlyModelViewSet
from .filters import IsHotFilterBackend
from rest_framework.decorators import detail_route, list_route
from .status import *
from general.settings import STATIC_URL
from django.template.response import TemplateResponse
from general.settings import JIE_DOMAIN
from .values import UI_conf, UI_conf_keys, coins_rules
from profiles.user_info import UserInfoMongo


class EarnCoinView(APIView):
    permission_classes = (IsCustomUser,)

    def get(self, request):
        # 应用缓存
        coin_configs = get_credit_coin_config()

        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        auth = user_info.auth
        auth.update({'has_shared_friends': int(user_info.has_shared_friends)})  # 分享朋友圈
        auth.update({'has_signed': int(user_info.has_signed)})  # 签到
        return Response({'data': coin_configs, 'auth': auth})


def coins_home_view(request):
    # print('coins', request.COOKIES.keys())
    context = {'static': STATIC_URL}
    return TemplateResponse(request, 'coins/index.html', context)


class CouponHomeView(APIView):
    permission_classes = (IsCustomUser,)

    def get(self, request):
        # print('CouponHomeView', request.COOKIES.keys())
        user_id = request.user_id

# banners_1
        banners_coupon = CouponBanner.objects.filter(is_active=True)
        data_banners = CouponBannerSerializer(banners_coupon, many=True).data

        # 资讯
        news_coupon = CouponNews.objects.filter(is_active=True)
        data_news = CouponNewsSerializer(news_coupon, many=True).data

        # coupon 分类
        category_credit = CouponType.objects.filter(is_active=True, is_birthday=False, is_new_register=False)[:4]
        data_credit = CouponTypeSerializer(category_credit, many=True).data

        # 新人专享分类
        category_register = CouponType.objects.filter(is_active=True, is_birthday=False, is_new_register=True)[:4]
        data_register = CouponTypeSerializer(category_register, many=True).data

        # 生日特权分类
        category_birthday = CouponType.objects.filter(is_active=True, is_birthday=True, is_new_register=False)[:4]
        data_birthday = CouponTypeSerializer(category_birthday, many=True).data

        # activity 活动产品
        activity = CouponActivity.objects.filter(is_active=True)[:2]
        data_activity = CouponActivitySerializer(activity, many=True).data

        UI_data_all = {
            'banner_coupon': data_banners,
            'news_coupon': data_news,
            'category_coupon_credit': data_credit,
            'category_coupon_register': data_register,
            'category_coupon_birthday': data_birthday,
            'activity': data_activity
        }

        ret_UI = []
        ret = {}

        # hardcoding UI 配置
        for type_name in UI_conf_keys:
            UI_obj = UI_conf.get(type_name, {})
            params_dict = UI_obj.get('params', {})
            num = params_dict.get('num')
            data = UI_data_all.get(type_name) or []
            if num:
                data = data[:num]

            type_data = {
                'type_name': type_name.split('_')[0],
                'params_dict': params_dict,
                'data': data
            }
            ret_UI.append(type_data)

        ret['UI'] = ret_UI
        ret["credit_coin_rule"] = coins_rules
        ret['user'] = get_user_coin_data(user_id)
        return Response(ret)


class CouponsView(ReadOnlyModelViewSet):
    serializer_class = CouponTypeSerializer
    filter_backends = [IsHotFilterBackend]
    queryset = CouponType.objects.filter(is_active=True)
    permission_classes = (IsCustomUser,)

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        serializer = CouponTypeSerializer(queryset, many=True)
        ret = {
            'ret': serializer.data
        }
        return Response(ret)

    def retrieve(self, request, *args, **kwargs):
        obj = CouponType.objects.get(id=self.kwargs['pk'])
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        ret = {}
        ret['tip'] = '兑换'
        ret['coupon'] = CouponTypeSerializer(obj).data
        validate = CouponTypeValidate(CouponTypeSerializer(obj).data)
        ret.update(validate.check_can_conver(user_info))
        return Response(ret)

    @detail_route(methods=['post'], permission_classes=(IsCustomUser,))
    def convert(self, request, pk):  # 信用币兑换券
        try:
            obj = CouponType.objects.get(id=pk)
        except CouponType.DoesNotExist:
            RaiseMessage().obj_not_exist()
        else:
            user_id = request.user_id
            user_info = UserInfoMongo(user_id)
            validate = CouponTypeValidate(CouponTypeSerializer(obj).data)

            check_can_convert = validate.check_can_conver(user_info)
            if not check_can_convert['enable']:
                RaiseMessage(check_can_convert['tip'])

            user_info.add_coupon(obj.id)
            if obj.credit_coin:
                user_info.update_coin('convert', -obj.credit_coin)

            ret = {}
            ret['msg'] = '兑换成功'
            ret['redbags_url'] = JIE_DOMAIN + '/misc/profiles/redbags'
            return Response(ret)  # 兑换完成，返回信用币首页，刷新用户信用币

    @detail_route(methods=['get'], permission_classes=(IsCustomUser,))
    def user_coupon(self, request, pk):  # 红包详情
        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        user_coupon = user_info.get_coupon(str(pk))
        coupon = user_coupon.get('coupon')
        if not coupon:
            RaiseMessage().coupon_status_error()

        validate = CouponTypeValidate(coupon)
        check_can_use = validate.check_can_use(user_info, user_coupon['user_created'], user_coupon['use_status'])
        check_coupon_time = validate.check_coupon_time(user_info, user_coupon['user_created'])
        time_effective = check_coupon_time['time_effective'] or '~'
        time_expire = check_coupon_time['time_expire'] or '~'

        if check_coupon_time['time_effective']:
            time_effective = time_effective.strftime('%Y-%m-%d %H:%M:%S')
        if check_coupon_time['time_expire']:
            time_expire = time_expire.strftime('%Y-%m-%d %H:%M:%S')

        ret = {
            'add_id': user_coupon['add_id'],
            'name': coupon['name'],
            'effective': check_can_use['enable'],
            'icon': coupon['icon'],
            'show_time': '有效期',
            'show_time_content': '%s - %s' % (time_effective, time_expire),
            'button_text': check_can_use['tip'],
            'show_condition': '使用条件',
            'show_condition_content': [],
            'usage_list': coupon['usage_list']
        }
        return Response(ret)

    @list_route(methods=['post'], permission_classes=(IsCustomUser,))
    def use(self, request):
        # device，暂停md5校验
        device = request.device
        serializer = CouponUseSerializer(data=request.data, device=device)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_id = request.user_id
        user_info = UserInfoMongo(user_id)
        # 检查是用户的
        add_id = data['add_id']
        user_coupon = user_info.get_coupon(add_id)
        coupon = user_coupon['coupon']
        if not user_coupon:
            RaiseMessage().coupon_is_expire()

        ret = {}

        # 检查能使用
        validate = CouponTypeValidate(coupon)
        check_can_use = validate.check_can_use(user_info, user_coupon['user_created'], user_coupon['use_status'])
        if not check_can_use['enable']:
            RaiseMessage(check_can_use['tip'])

        # 手机话费
        is_phone = coupon.get('is_phone', False)
        is_phone_flow = coupon.get('is_phone_flow', False)
        is_credit_coin = coupon.get('is_credit_coin', False)
        # 前端先返回使用成功，但状态为使用中；异步任务完成后再更新为使用成功或使用失败
        if is_phone:
            money = int(coupon['phone_amount']/100)
            user_info.update_coupon(add_id, USING)
            # 发送到market 执行，暂停话费充值功能
            # task_longju_huafei.delay(add_id, user.number, money)

            ret = {'msg': '使用成功'}
        # 手机流量
        elif is_phone_flow:
            money = int(coupon['phone_amount']/100)
            user_info.update_coupon(add_id, USING)
            # 发送到market 执行，暂停话费充值功能
            # task_longju_flow.delay(add_id, user.number, money)
            ret = {'msg': '使用成功'}

        # 信用币
        elif is_credit_coin:
            coin = coupon['credit_coin_amount']
            user_info.update_coupon(add_id, USED)
            user_info.update_coin(case='add_id', custom_num=coin, add_id=add_id)

            ret = {'msg': '使用成功'}
        else:
            RaiseMessage().obj_not_exist()

        return Response(ret)
