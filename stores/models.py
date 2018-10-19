from django.db import models
from jsonfield import JSONField
from profiles.values import credit_result
from .values import coupon_section_choices
from datetime import datetime, timedelta
from common.datecount import str_to_datetime
from .status import *


class CreditCoinConfig(models.Model):
    name = models.CharField(max_length=36, verbose_name='名称')  # 如：
    uid = models.CharField(max_length=24, unique=True, default='', verbose_name='字段标记')
    desc = models.CharField(max_length=64, verbose_name='描述')
    icon = models.ImageField(upload_to='stores/icon', verbose_name='图标')
    credit_coin_amount = models.PositiveIntegerField(default=0, verbose_name='奖励信用币', help_text='单位：个')
    is_continue = models.BooleanField(default=False, verbose_name='可重复任务', help_text='例如邀请好友任务，每天可以做多次')
    rank = models.PositiveIntegerField(default=0, verbose_name='排序', help_text='数值越大越靠前', db_index=True)
    json_event = JSONField(verbose_name='跳转', null=True, blank=True, help_text='格式:{}，约定跳转到原生页面')
    is_active = models.BooleanField(default=False, verbose_name='是否生效')

    class Meta:
        ordering = ['-rank']
        verbose_name = '赚信用币'
        verbose_name_plural = verbose_name


class CouponType(models.Model):
    """
    目前的券类型：话费、流量、信用币
    """

    name = models.CharField(max_length=36, verbose_name='名称')  # 如：10元话费
    sub_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='副标题(选填)')
    desc = models.CharField(max_length=64, verbose_name='备注')
    icon = models.ImageField(upload_to='stores/icon', verbose_name='图标')
    json_detail = JSONField(null=True, verbose_name='权益介绍', help_text='["介绍2", "介绍1"]')
    json_usage = JSONField(null=True, verbose_name='使用方法', help_text='["使用 a", "使用 b"]')
    # 话费、流量充值
    is_phone = models.BooleanField(default=False, verbose_name='是否话费充值')
    is_phone_flow = models.BooleanField(default=False, verbose_name='是否手机流量充值')
    phone_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='话费/流量金额', help_text='单位：分，10元填1000，充流量时只支持：1000，3000，5000')
    # 信用币奖励
    is_credit_coin = models.BooleanField(default=False, verbose_name='是否是奖励信用币')
    credit_coin_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='奖励信用币', help_text='单位：个')
    # 配置
    rank = models.PositiveIntegerField(default=0, verbose_name='排序', help_text='数值越大越靠前', db_index=True)
    is_hot = models.BooleanField(default=False, verbose_name='热门')
    is_active = models.BooleanField(default=False, verbose_name='是否生效')
    # 权益（话费、）、投资券、借款券
    section = models.CharField(max_length=16, choices=coupon_section_choices, default='credit', verbose_name='券类型')
    # 限制条件
    only_once_year = models.BooleanField(default=False, verbose_name='一年只能领取一次', help_text='对生日礼包，节日礼包等，要限制为1次，一年一次')
    only_once_ever = models.BooleanField(default=False, verbose_name='一人只能领取一次', help_text='对新人礼包等，要限制为1次，从此不能再领')
    credit_coin = models.PositiveIntegerField(default=0, verbose_name='消耗信用币数量')
    level_min = models.CharField(max_length=4, null=True, blank=True, verbose_name='信用等级要求', help_text='例如 B（做过身份证和手机号认证），不填表示对信用等级没有要求')  # 如：B
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始日期', help_text='可选')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束日期', help_text='可选')
    effective_days = models.IntegerField(null=True, blank=True, verbose_name='有效天数')
    is_new_register = models.BooleanField(default=False, verbose_name='新人专享', help_text='注册7天内')
    is_birthday = models.BooleanField(default=False, verbose_name='生日专享', help_text='只在生日当天可以使用，一年最多领一次')

    class Meta:
        ordering = ['-rank']
        verbose_name = '优惠券类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name + self.desc

    @property
    def event_action(self):
        return {
            'link': '',
            'link_detail': True,
            'name': self.name,
            'coupon_id': self.id
        }


class CouponTypeValidate(object):   # 用于mongodb数据判断，防止 obj 数值更改

    def __init__(self, coupon_data):
        self.coupon_data = coupon_data

    # def check_get_new_register(self, user):


    def check_use_status(self, use_status):
        if use_status == GOT:
            return {
                'enable': True,
                'tip': '去使用'
            }
        elif use_status == USEFAILED:
            return {
                'enable': True,
                'tip': '重新使用'
            }
        else:
            return {
                'enable': False,
                'tip': status_str[use_status]
            }

    def check_coupon_time(self, user_info, user_created=None):
        """
        检查时间：
        :param user: 
        :param user_created: 
        :return: 
        """
        effective = True
        time_effective = None
        expire = False
        time_expire = None

        start_time = self.coupon_data.get('start_time')
        end_time = self.coupon_data.get('end_time')
        is_birthday = self.coupon_data.get('is_birthday', False)
        is_new_register = self.coupon_data.get('is_new_register')
        effective_days = self.coupon_data.get('effective_days')

        if start_time:
            start_time_d = datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
            # start_time_d = start_time
            if datetime.now() < start_time_d:
                effective = False

            time_ef = start_time_d
            time_effective = max(time_effective, time_ef) if time_effective else time_ef

        if end_time:
            end_time_d = datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S')
            # end_time_d = end_time
            if datetime.now() > end_time_d:
                expire = True

            time_ex = end_time_d
            time_expire = min(time_expire, time_ex) if time_expire else time_ex

        if is_birthday:
            if not user_info.is_birthday:
                effective = False
                expire = True

            # 检查今天领过

            if user_info.birthday:

                today = datetime.today()
                time_ex = datetime(year=today.year, month=today.month, day=today.day) + timedelta(hours=23, minutes=59, seconds=59)
                time_expire = min(time_expire, time_ex) if time_expire else time_ex
                if user_created:
                    time_ef = datetime(year=user_created.year, month=user_info.birthday.month, day=user_info.birthday.day)
                    time_effective = max(time_effective, time_ef) if time_effective else time_ef
            else:
                effective = False
                expire = True

        if is_new_register:
            if not user_info.is_new_register:
                effective = False
                expire = True
            else:
                time_ex = user_info.date_joined + timedelta(days=7, seconds=-1)
                time_expire = min(time_expire, time_ex) if time_expire else time_ex

        if effective_days and user_created:
            delta = datetime.now() - user_created
            if delta.days > effective_days:
                expire = True

            time_ex = user_created + timedelta(days=effective_days, seconds=-1)
            time_expire = min(time_expire, time_ex) if time_expire else time_ex

        ret = {
            'effective': effective,
            'time_effective': time_effective,
            'expire': expire,
            'time_expire': time_expire
        }
        return ret

    # 币兑券
    def check_can_conver(self, user_info, user_created=None):
        """
        兑换检查：1、生效 2、失效 3、用户信用币 4、信用等级
        :param user: 
        :param use_status: 
        :param user_created: 
        :return: 
        """

        check_time = self.check_coupon_time(user_info, user_created)
        enable = True
        tip = '立即兑换'
        need_coin_num = self.coupon_data.get('credit_coin')
        level_min = self.coupon_data.get('level_min')
        if not check_time['effective']:
            enable = False
            tip = '活动未生效'
        elif check_time['expire']:
            enable = False
            tip = '活动已经过期'
        elif need_coin_num and user_info.credit_coin < need_coin_num:
            enable = False
            tip = '信用币不足'
        elif user_info.check_re_got(self.coupon_data['id']):
            enable = False
            tip = '已经领过啦'
        elif level_min and not user_info.check_credit_rank(level_min):
            enable = False
            tip = '信用等级不够，去提高信用'

        return {
            'enable': enable,
            'tip': tip
        }

    def check_can_use(self, user, user_created, use_status):
        """
        使用检查： 1、生效 2、失效 3、红包状态
        :param user: 
        :param user_created: 
        :param use_status: 
        :return: 
        """
        check_time = self.check_coupon_time(user, user_created)
        check_use = self.check_use_status(use_status)
        level_min = self.coupon_data.get('level_min')
        if not check_time['effective']:
            enable = False
            tip = '待生效'
        elif check_time['expire']:
            enable = False
            tip = '已过期'
        elif level_min and not user.check_credit_rank(level_min):
            enable = False
            tip = '信用等级不够'
        else:
            enable = check_use['enable']
            tip = check_use['tip']

        return {
            'enable': enable,
            'tip': tip
        }


# BaseRedBagConfig
class BaseCouponConfig(models.Model):
    created = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(CouponType, null=True, verbose_name='选择券', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name='是否生效')

    class Meta:
        abstract = True

    @property
    def event_action(self):
        return {
            'link_detail': True,
            'link': '',
            'coupon_id': self.coupon.id,
            'name': self.coupon.name
        }


class CouponNews(BaseCouponConfig):
    detail = models.CharField(max_length=128, verbose_name='消息', help_text='小***明 兑换了10元话费')

    class Meta:
        verbose_name = '大家在换-头条'
        verbose_name_plural = verbose_name


class CouponBanner(BaseCouponConfig):
    image = models.ImageField(upload_to='stores/banner', verbose_name='图片')
    desc = models.CharField(max_length=128, blank=True, null=True, verbose_name='描述')
    rank = models.PositiveIntegerField(default=0, verbose_name='排序', help_text='数值越大越靠前')
    # banner_UI = models.ForeignKey('pds.HomeUI', null=True, verbose_name='横幅类型', on_delete=models.CASCADE)
    banner_UI = JSONField(null=True, verbose_name='横幅配置', help_text='{"up": 16}等')

    class Meta:
        ordering = ['-rank']
        verbose_name = '信用币首页-横幅'
        verbose_name_plural = verbose_name


class CouponActivity(BaseCouponConfig):
    desc = models.CharField(max_length=128, blank=True, null=True, verbose_name='描述')
    pic = models.ImageField(upload_to='stores/activity', null=True, blank=True, verbose_name='活动图片')  # 对应一种类型
    rank = models.PositiveIntegerField(default=0, verbose_name='排序', help_text='数值越大越靠前')

    class Meta:
        ordering = ['-rank']
        verbose_name = '首页-活动'
        verbose_name_plural = verbose_name


# platagent 类似
# class CouponConfig(models.Model):

