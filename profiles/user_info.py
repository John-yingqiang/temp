from django.utils.functional import cached_property
from common.mongo import mongodb
from pymongo import MongoClient, ReturnDocument
from datetime import datetime, timedelta, date
from common.redis_client import rc
import bson
from .credit_level import CreditCoin, CreditScore, CreditAmount, AppraisalCreditLevel
from utils.invite_code import InviteCode
import time
from stores.status import *
from .values import *


class UserInfoMongo(object):

    def __init__(self, user_id):
        self.user_id = int(str(user_id))

# TODO(ChenQiushi): 内网接口，获取用户 model 信息：date_joined，number
    @property
    def model_info(self):    # users mongodb
        return {}

    @property
    def users(self):    # users mongodb
        return mongodb.users.find_one({'_id': self.user_id}) or {}

# profile 来自 base 或 mongo

    @property
    def profile(self):
        profile_list = self.users.get('profile', [])
        data = {}
        if profile_list:
            for p in profile_list:
                data.update(p)
        return data

    def update_profile(self, data, from_proj=None):
        data['timestamp'] = int(time.time())
        mongodb.users.update_one({'_id': self.user_id}, {'$push': {'profile': data}}, upsert=True)

        # if from_proj == 'jie':
        #     self.update_auth(jie_profile=1)

    @property
    def nickname(self):
        return self.profile.get('nickname', '')

    @property
    def avatar_url(self):
        return self.profile.get('avatar_url', '')

    @property
    def province(self):
        return self.profile.get('province', '')

    @property
    def city(self):
        return self.profile.get('city', '')

    @property
    def express_address(self):
        return self.profile.get('express_address', '')

    @property
    def qq(self):
        return self.profile.get('qq', '')

    @property
    def job(self):
        return self.profile.get('job', '')

# user_mongo
    @cached_property
    def fake_profile(self):
        return self.users.get('fake_profile', {})

    def update_fake_profile(self, fake_data):
        updates = {}
        for k, v in fake_data.items():
            updates['fake_profile.' + k] = v

        if updates:
            mongodb.users.update_one({'_id': self.user_id}, {'$set': updates}, upsert=True)

# 邀请码，邀请好友
    @cached_property
    def invite_code(self):
        return InviteCode().uid_to_code(self.user_id)

# 认证
    # 认证信息
    @property
    def auth(self):
        return self.users.get('auth', {})

    def update_auth(self, data):
        updates = {}
        timestamp = int(time.time())
        for k, v in data.items():
            updates['auth.'+k] = v
            updates['auth.last_updates.'+k] = timestamp

        mongodb.users.update_one({'_id': self.user_id}, {'$set': updates}, upsert=True)

    @property
    def identification(self):
        # TODO(ChenQiushi): 身份证
        return ''

    # 信用分
    @property
    def credit_score(self):
        return CreditScore(self).calculate()

    # 信用额度
    @property
    def credit_amount(self):
        return CreditAmount(self).calculate()

# 兼容 v3.4
    @property
    def credit_data(self):
        return self.users.get('credit_data', {})

    def update_credit_data(self, case, data):
        mongodb.users.update_one({'_id': self.user_id}, {'$set': {'credit_data.%s' % case: data}}, upsert=True)
        self.update_credit_level_data()

    @property
    def credit_level_data(self):
        return self.users.get('credit_level_data') or credit_result['D']

    def update_credit_level_data(self):
        credit_level_data = AppraisalCreditLevel(self.credit_data).appraisal()
        mongodb.users.update_one({'_id': self.user_id}, {'$set': {'credit_level_data': credit_level_data}}, upsert=True)

    def check_credit_rank(self, credit_level):
        return self.credit_level_data['rank'] >= credit_result[credit_level]['rank']

    @property
    def credit_level(self):
        return self.credit_level_data['level']

# 信用币
# 用户信息
    @property
    def is_new_register(self):  # 新人专享，注册后7天内
        # now = datetime.now()
        # TODO(ChenQiushi): 从 users model 获取信息
        # delta = now - self.model_info.get('date_joined')
        # return delta.days < 8
        return False

    @property
    def birthday(self):  # 生日、有生日活动，不能更改
        if self.identification:
            return date.today().replace(int(self.identification[6:10]), int(self.identification[10:12]), int(self.identification[12:14]))
        return None

    @property
    def is_birthday(self):  # 生日专享，注册后7天内
        if self.birthday:
            today = datetime.today()
            return today.month == self.birthday.month and today.day == self.birthday.day
        return False

    @property
    def gender(self):
        ret = '未知'
        cert = self.identification
        if cert:
            ret = '女' if int(cert[16]) % 2 is 0 else '男'
        return ret

    # 签到
    @property
    def has_signed(self):  # 是否已经签到
        return CreditCoin(self).has_signed()

    @property
    def to_sign_coin(self):  # 签到奖励信用币
        return CreditCoin(self).sign_to_get()

    def sign_in(self):  # 签到
        CreditCoin(self).user_sign()

    def check_invite_code(self, apply):
        """
        只在新增用户时调用
        A 邀请 B
        A 增加记录：add_share_register， B 增加记录：add_share_friend
        :param apply:
        :return:
        """
        if apply.invite_code:
            CreditCoin(self).add_share_register(apply.invite_code)
            user_id = InviteCode().code_to_uid(apply.invite_code)
            if user_id:
                user_from_info = UserInfoMongo(user_id)
                CreditCoin(user_from_info).add_share_friend(self.user_id)

    # 通过邀请码登录
    @property
    def has_from_invite(self):  # 是否已经获得过邀请码注册奖励
        invite_code = self.users.get('login_from_invite')
        return invite_code is not None

    def update_from_invite(self, invite_code):
        mongodb.users.update_one({'_id': self.user_id}, {'$set': {'login_from_invite': invite_code}}, upsert=True)

    @property
    def invite_list(self):
        return self.users.get('invite_list') or []

    def update_invite_list(self, friend_id):
        mongodb.users.update_one({'_id': self.user_id}, {'$push': {'invite_list': friend_id}}, upsert=True)

    @property
    def credit_coin(self):
        return self.users.get('credit_coin', 0)

    def update_credit_coin(self, num):
        mongodb.users.update_one({'_id': self.user_id}, {'$inc': {'credit_coin': num}}, upsert=True)

    def update_coin(self, case, custom_num=0, user_id=None, add_id=None):  # 增加信用币
        """
        :param case: (sign, share, identification, number, zhima, gongjijin, add_id)
        :param num:
        :param user_id:
        :param add_id: 通过红包获得
        :return:
        """
        # 还有用户分享的奖励
        if custom_num:
            self.update_credit_coin(custom_num)
        mongodb.users.update_one({'_id': self.user_id}, {'$push': {'coin_history.%s' % case: custom_num}}, upsert=True)

# 信用币任务状态
    # 每日邀请任务
    @property
    def has_shared_friends(self):
        return rc.get('update_share_friends_' + str(self.user_id)) is '1'.encode()

    def update_share_friends(self):
        if not rc.get('update_share_friends_' + str(self.user_id)):
            now = datetime.now()
            today = datetime.today()
            time_pass = (now - datetime(year=today.year, month=today.month, day=today.day)).seconds
            seconds_left = 24*3600 - time_pass
            rc.set('update_share_friends_' + str(self.user_id), '1', seconds_left)
            CreditCoin(self).add_shared_task()

# 优惠券
    @property
    def coupons(self):
        return self.users.get('coupons', [])

    def get_coupon(self, add_id):
        for coupon in self.coupons:
            if coupon['add_id'] == add_id:
                print('get', add_id)
                return coupon
        return None

    def update_got_once_year(self, coupon_id):
        rc.set('update_got_once_year_%s_%s' % (self.user_id, coupon_id), 1, 364*24*3600)
        if self.identification:
            rc.set('update_got_once_year_%s_%s' % (self.identification, coupon_id), 1, 364*24*3600)

    def check_got_once_year(self, coupon_id):  # 同一个手机号、身份证只能领取一次
        if rc.get('update_got_once_year_%s_%s' % (self.user_id, coupon_id)):
            return True
        if self.identification:
            if rc.get('update_got_once_year_%s_%s' % (self.identification, coupon_id)):
                return True
        return False

# 只能获取一次的奖励
    def update_got_once_ever(self, coupon_id):
        rc.set('update_got_once_ever_%s_%s' % (self.user_id, coupon_id), 1)
        if self.identification:
            rc.set('update_got_once_ever_%s_%s' % (self.identification, coupon_id), 1)

    def check_got_once_ever(self, coupon_id):
        if rc.get('update_got_once_ever_%s_%s' % (self.user_id, coupon_id)):
            return True
        if self.identification:
            if rc.get('update_got_once_ever_%s_%s' % (self.identification, coupon_id)):
                return True
        return False

    def check_re_got(self, coupon_id):
        return self.check_got_once_ever(coupon_id) or self.check_got_once_year(coupon_id)

    def add_coupon(self, coupon_id):  # 加密，币兑券
        from stores.serializers import CouponTypeSerializer
        from stores.models import CouponType
        coupon = CouponType.objects.get(id=coupon_id)
        if coupon.only_once_year:
            self.update_got_once_year(coupon_id)
        if coupon.only_once_ever:
            self.update_got_once_ever(coupon_id)

        data = {
            'add_id': str(bson.ObjectId()),
            'coupon': CouponTypeSerializer(coupon).data,
            'use_status': GOT,
            'user_created': datetime.now(),
            'last_updates': {
                'use_status'+str(GOT): int(time.time())
            }
        }
        mongodb.users.update_one({'_id': self.user_id}, {'$push': {'coupons': data}}, upsert=True)
        return data['add_id']

    def update_coupon(self, add_id, use_status, handler=False):
        updates_data = {
            'coupons.$.use_status': use_status,
            'coupons.$.last_updates.%s' % ('use_status'+str(use_status)): int(time.time())
        }
        mongodb.users.update_one({'_id': self.user_id, 'coupons.add_id': add_id}, {'$set': updates_data})

    def delete_coupon(self, add_id):  # 券失效或者使用成功后，在用户访问时检查删除
        mongodb.users.update({'_id': self.user_id}, {'$pull': {'coupons': {'add_id': add_id}}})

# 论坛
    @property
    def topic_messages(self):
        return mongodb.users.find_one({'_id': self.user_id}, projection={'topic_message': True, '_id': False}) or {'topic_message': []}

    def add_topic_messages(self, message):
        # 保留最近30条消息
        mongodb.users.update_one({'_id': self.user_id},
                                 {'$push': {'topic_message': {'$each': [message], '$position': 0, '$slice': 30}},},
                                 upsert=True)

    def unread_message_nums(self):
        topic_nums = mongodb.users.find_one({'_id': self.user_id}, projection={'unread_topic_nums': 1, '_id': False}) or {}
        return topic_nums.get('unread_topic_nums', 0)

    def update_unread_topic_message(self, count=None):
        inc_num = count or 1
        mongodb.users.update_one({'_id': self.user_id}, {'$inc': {'unread_topic_nums': inc_num}}, upsert=True)

    def read_topic_messages(self):
        mongodb.users.update_one({'_id': self.user_id}, {'$set': {'unread_topic_nums': 0}}, upsert=True)
