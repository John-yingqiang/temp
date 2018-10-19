from django.test import TestCase, modify_settings
from django.test import Client
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string
import os

from profiles.tests.utils import UserClient
from stores.models import *
from stores.serializers import CouponTypeSerializer
from datetime import datetime, timedelta


class TestLiveView(TestCase):
    serialized_rollback = True

    def setUp(self):

        pass

    """
        name = models.CharField(max_length=36, verbose_name='名称')  # 如：10元话费
        desc = models.CharField(max_length=64, verbose_name='备注')
        icon = models.ImageField(upload_to='coins/icon', verbose_name='图标')

        # 话费、流量充值
        is_phone = models.BooleanField(default=False, verbose_name='是否话费充值')
        is_phone_flow = models.BooleanField(default=False, verbose_name='是否手机流量充值')
        phone_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='话费/流量金额', help_text='单位：分，10元填1000，充流量时只支持：1000，3000，5000')
        # 信用币奖励
        is_credit_coin = models.BooleanField(default=False, verbose_name='是否是奖励信用币')
        credit_coin_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='奖励信用币', help_text='单位：个')
        # 配置
        is_hot = models.BooleanField(default=False, verbose_name='热门')
        is_active = models.BooleanField(default=False, verbose_name='是否生效')
        # 权益（话费、）、投资券、借款券
        section = models.CharField(max_length=16, choices=coupon_section_choices, default='credit', verbose_name='券类型')
        # 限制条件
        only_once_year = models.BooleanField(default=False, verbose_name='一年只能领取一次', help_text='对生日礼包，节日礼包等，要限制为1次，一年一次')
        only_once_ever = models.BooleanField(default=False, verbose_name='一人只能领取一次', help_text='对新人礼包等，要限制为1次，从此不能再领')
        credit_coin = models.PositiveIntegerField(default=0, verbose_name='消耗信用币数量')
        level_min = models.CharField(max_length=4, choices=tuple((key, key) for key in credit_result.keys()), null=True, blank=True, verbose_name='信用等级要求')  # 如：B
        start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始日期', help_text='可选')
        end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束日期', help_text='可选')
        effective_days = models.IntegerField(null=True, blank=True, verbose_name='有效天数')
        is_new_register = models.BooleanField(default=False, verbose_name='新人专享', help_text='注册7天内')
        is_birthday = models.BooleanField(default=False, verbose_name='生日专享', help_text='只在生日当天可以使用，一年最多领一次')
    """
    def test_register(self):
        """
         测试新人专享
        :return: 
        """
        coupon_new, created = CouponType.objects.get_or_create(name='is_new_register', is_new_register=True, defaults={'desc': 'desc'})
        coupon_default, created = CouponType.objects.get_or_create(name='is_not_new_register', is_new_register=False,
                                                           defaults={'desc': 'desc'})
        user_new, created = User.objects.get_or_create(number='10661111111')
        user_old, created = User.objects.get_or_create(number='10661111113')
        user_old.date_joined = datetime(year=1991, month=1, day=1)
        validate = CouponTypeValidate(CouponTypeSerializer(coupon_new).data)
        ret = validate.check_can_conver(user_new)
        self.assertTrue(ret['enable'])
        self.assertEqual(ret['tip'], '立即兑换')
        ret = validate.check_can_conver(user_old)
        self.assertFalse(ret['enable'])
        self.assertEqual(ret['tip'], '活动未生效')

        validate = CouponTypeValidate(CouponTypeSerializer(coupon_default).data)
        ret = validate.check_can_conver(user_new)
        self.assertTrue(ret['enable'])
        self.assertEqual(ret['tip'], '立即兑换')
        ret = validate.check_can_conver(user_old)
        self.assertTrue(ret['enable'])
        self.assertEqual(ret['tip'], '立即兑换')

    def test_birthday(self):
        """
        测试生日特权
        :return: 
        """
        coupon_new, created = CouponType.objects.get_or_create(name='is_birthday', is_birthday=True, defaults={'desc': 'desc'})
        coupon_default, created = CouponType.objects.get_or_create(name='is_not_birthday', is_birthday=False,
                                                           defaults={'desc': 'desc'})
        user_is, created = User.objects.get_or_create(number='10661111111')
        user_not, created = User.objects.get_or_create(number='10661111113')
        today = datetime.today()
        id_time = '3213231991'
        id_time = id_time + '0' + str(today.month) if today.month < 10 else id_time + str(today.month)
        id_time = id_time + '0' + str(today.day) if today.day < 10 else id_time + str(today.day)
        user_is.identification = id_time + '0009'
        validate = CouponTypeValidate(CouponTypeSerializer(coupon_new).data)
        ret = validate.check_can_conver(user_is)
        self.assertTrue(ret['enable'])
        self.assertEqual(ret['tip'], '立即兑换')
        ret = validate.check_can_conver(user_not)
        self.assertFalse(ret['enable'])
        self.assertEqual(ret['tip'], '活动未生效')

        validate = CouponTypeValidate(CouponTypeSerializer(coupon_default).data)
        ret = validate.check_can_conver(user_is)
        self.assertTrue(ret['enable'])
        self.assertEqual(ret['tip'], '立即兑换')
        ret = validate.check_can_conver(user_not)
        self.assertTrue(ret['enable'])
        self.assertEqual(ret['tip'], '立即兑换')

    def test_special_time(self):
        """
        测试指定时间
        :return: 
        """
        coupon_new, created = CouponType.objects.get_or_create(name='is_birthday',
                                                               is_birthday=True,
                                                               start_time=datetime.now(),
                                                               end_time=datetime.now()+timedelta(days=2),
                                                               defaults={'desc': 'desc'}
                                                               )
        coupon_default, created = CouponType.objects.get_or_create(name='is_not_birthday', 
                                                                   is_birthday=False, 
                                                                   start_time=datetime.now()+timedelta(days=1),
                                                                   end_time=datetime.now()+timedelta(days=2),
                                                                   defaults={'desc': 'desc'})
        user_is, created = User.objects.get_or_create(number='10661111111')
        user_not, created = User.objects.get_or_create(number='10661111113')
        today = datetime.today()
        id_time = '3213231991'
        id_time = id_time + '0' + str(today.month) if today.month < 10 else id_time + str(today.month)
        id_time = id_time + '0' + str(today.day) if today.day < 10 else id_time + str(today.day)
        user_is.identification = id_time + '0009'
        validate = CouponTypeValidate(CouponTypeSerializer(coupon_new).data)
        ret = validate.check_can_conver(user_is)
        self.assertTrue(ret['enable'])
        self.assertEqual(ret['tip'], '立即兑换')
        ret = validate.check_can_conver(user_not)
        self.assertFalse(ret['enable'])
        self.assertEqual(ret['tip'], '活动未生效')

        validate = CouponTypeValidate(CouponTypeSerializer(coupon_default).data)
        ret = validate.check_can_conver(user_is)
        self.assertFalse(ret['enable'])
        self.assertEqual(ret['tip'], '活动未生效')
        ret = validate.check_can_conver(user_not)
        self.assertFalse(ret['enable'])
        self.assertEqual(ret['tip'], '活动未生效')

    def test_expire(self):
        user_is, created = User.objects.get_or_create(number='10661111111')
        c = UserClient()
        number = "100" + get_random_string(8, allowed_chars="0123456789")
        user = User.objects.create_user(number=number, password='111111')
        user.credit_coin = 1000
        user.save()
        c.dai_login(user)
        self.user_client = c

        coupon_new, created = CouponType.objects.get_or_create(name='is_test_expire',
                                                               start_time=datetime.now(),
                                                               credit_coin=100,
                                                               end_time=datetime.now() + timedelta(days=10),
                                                               defaults={'desc': 'desc'}
                                                               )
        coupon_default, created = CouponType.objects.get_or_create(name='is_not_test_expire',
                                                                   start_time=datetime(year=1991, month=1, day=1),
                                                                   end_time=datetime(year=1991, month=1, day=2),
                                                                   defaults={'desc': 'desc'})

        url_s = '/api/coins/%s/convert' % str(coupon_default.id)
        r = self.user_client.post(url_s, {})
        ret = r.json()
        self.assertEqual(ret['msg'], '活动已经过期')

        url_s = '/api/coins/%s/convert' % str(coupon_new.id)
        r = self.user_client.post(url_s, {})
        ret = r.json()

        self.assertEqual(ret['msg'], '兑换成功')
        user_now = User.objects.get(id=user.id)
        self.assertEqual(user_now.credit_coin, 900)

    def test_use(self):
        coupon_coin, created = CouponType.objects.get_or_create(name='is_coin',
                                                                is_credit_coin=True,
                                                                credit_coin_amount=9,
                                                               start_time=datetime.now(),
                                                               end_time=datetime.now() + timedelta(days=2),
                                                               defaults={'desc': 'desc'}
                                                               )
        coupon_phone, created = CouponType.objects.get_or_create(name='is_phone',
                                                                is_phone=True,
                                                                 phone_amount=100,  # 1元话费
                                                               start_time=datetime.now(),
                                                               end_time=datetime.now() + timedelta(days=2),
                                                               defaults={'desc': 'desc'}
                                                               )
        coupon_flow, created = CouponType.objects.get_or_create(name='is_flow',
                                                                is_phone_flow=True,
                                                                 phone_amount=1000,  # 10元流量
                                                               start_time=datetime.now(),
                                                               end_time=datetime.now() + timedelta(days=2),
                                                               defaults={'desc': 'desc'}
                                                               )

        c = UserClient()
        number = '13162033009'
        user = User.objects.create_user(number=number, password='111111')
        user.credit_coin = 1000
        user.save()
        c.dai_login(user)
        self.user_client = c

        # add_coin = user.add_coupon(coupon_coin.id)
        # add_phone = user.add_coupon(coupon_phone.id)
        add_flow = user.add_coupon(coupon_flow.id)
        print('user', user.id)
        # print('add coin, phone, flow', add_coin, add_phone, add_flow)
        # r = self.user_client.post('/api/coupons/use', {'add_id': add_coin, 'sign': 's'})
        # print('use coin', r.json())
        # user_now = User.objects.get(id=user.id)
        # self.assertEqual(user_now.credit_coin, 1009)

        # command 检查充值 和 handler
        # r = self.user_client.post('/api/coupons/use', {'add_id': add_phone, 'sign': 's'})
        # print('use coin', r.json())
        # user_now = User.objects.get(id=user.id)
        # 检查券 used 被删除

        # r = self.user_client.post('/api/coupons/use', {'add_id': add_phone, 'sign': 's'})
        # print('use coin', r.json())
        #
        # r = self.user_client.post('/api/coupons/use', {'add_id': add_phone, 'sign': 's'})
        # print('use coin', r.json())

        r = self.user_client.post('/api/coupons/use', {'add_id': add_flow, 'sign': 's'})
        print('use coin', r.json())

        # # 连续两次提交，会被锁定
        # r = self.user_client.post('/api/coupons/use', {'add_id': add_flow, 'sign': 's'})
        # print('use coin', r.json())




