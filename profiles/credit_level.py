from .values import credit_cases, credit_result, sign_history_key
from common.redis_client import rc
from common.datecount import DateTimeCount
from .values import auth_scores
from stores.serializers import get_credit_coin_config


class AppraisalCreditLevel(object):

    def __init__(self, credit_data):
        self.credit_data = credit_data

    def appraisal(self):
        zhima = self.credit_data.get(credit_cases.zhima)
        if zhima:
            score = zhima.get('score')
            if score > 550:
                return credit_result['BB']
        number = self.credit_data.get(credit_cases.number)
        if number:
            return credit_result['B']
        identification = self.credit_data.get(credit_cases.identification)
        if identification:
            return credit_result['C']
        return credit_result['D']


class CreditScore(object):

    def __init__(self, user_info):
        self.user_info = user_info

    def calculate(self):
        """
        实时计算
        :return: 
        """
        # TODO(ChenQiushi): mongodb geo 存储分析地理位置

        auth = self.user_info.auth
        status_pass = [1, 10]

        # 肖像认证未通过，直接返回
        if not auth.get('identification', 0) in status_pass:
            return 0

        score = 350
        for auth_name in auth_scores.keys():
            if auth.get(auth_name, 0) in status_pass:
                score += auth_scores[auth_name]

        return score


class CreditAmount(object):
    """
    信用额度
    根据分数范围确定
    """

    def __init__(self, user):
        self.user = user

    def calculate(self):
        score = CreditScore(self.user).calculate()
        if score < 350:
            return 25000
        elif score < 450:
            return 25500
        elif score < 550:
            return 27000
        elif score < 600:
            return 29000
        else:
            return 32000


class CreditCoin(object):
    """
    信用币
    """

    def __init__(self, user_info):
        self.user_info = user_info
        self.redis_auth_key = 'user_credit_coins_'
        self.redis_sign_key = 'user_sign_coins_'+str(self.user_info.user_id)

# 认证
    def add_auth_coin(self, auth_name, auth_status):
        # 认证增加信用币，只增加一次

        status_pass = [1, 10]

        if auth_status not in status_pass or rc.setbit(self.redis_auth_key + auth_name, self.user_info.user_id, 1):
            return

        coin_config = get_credit_coin_config()
        for conf in coin_config:
            if conf['uid'] == auth_name:
                self.user_info.update_coin(auth_name, conf['credit_coin_amount'])
                break

# 签到
    def sign_to_get(self):
        """
        连续签到：第一天1个，第二天2个，三：4，四：6，五：8，六：10
        :return: 
        """
        days = DateTimeCount().days
        # 天数
        coin_can = 0
        for i in range(1, 6):
            if rc.getbit(self.redis_sign_key, days-i):
                coin_can += 2
            else:
                break

        return 1 if not coin_can else coin_can

    def user_sign(self):
        days = DateTimeCount().days
        if not rc.setbit(self.redis_sign_key, days, 1):
            self.user_info.update_coin('sign', self.sign_to_get())
            # TODO(ChenQiushi): 签到后，push 通知
            # self.user_info.push_msg('sign_after_a')

    def has_signed(self, days=None):
        days_now = DateTimeCount().days
        if days:
            days_now = days
        return rc.getbit(self.redis_sign_key, days_now)

# 邀请好友
    def add_share_register(self, invite_code):
        """
        a 邀请 b，b 登录后b等到奖励
        :param invite_code: 
        :return: 
        """
        if not self.user_info.has_from_invite:
            coin_config = get_credit_coin_config()
            for conf in coin_config:
                if conf['uid'] == 'share':
                    self.user_info.update_coin('share', conf['credit_coin_amount'])
                    break
        self.user_info.update_from_invite(invite_code)

    def add_share_friend(self, friend_id):
        """
        a 邀请 b，a 获得奖励
        邀请好友，获得奖励
        :param friend_id: 注册用户 id
        :return: 
        """
        if friend_id not in self.user_info.invite_list:
            coin_config = get_credit_coin_config()
            for conf in coin_config:
                if conf['uid'] == 'share':
                    self.user_info.update_coin('share', conf['credit_coin_amount'])
                    break

        self.user_info.update_invite_list(friend_id)

    def add_shared_task(self):
        """
        每日分享朋友圈任务
        :param friend_id: 注册用户 id
        :return: 
        """
        if self.user_info.has_shared_friends:
            return

        coin_config = get_credit_coin_config()
        for conf in coin_config:
            if conf['uid'] == 'has_shared_friends':
                self.user_info.update_coin('has_shared_friends', conf['credit_coin_amount'])
                break

# 好友成功借款

# 下载借款
    def add_download_dai(self, product_id):
        """
        下载贷款产品，去重
        :param product_id: 
        :return: 
        """
        coin_config = get_credit_coin_config()
        for conf in coin_config:
            if conf['uid'] == 'download_product':
                self.user_info.update_coin('download_product', conf['credit_coin_amount'])
                break

# 申请信用卡

# 论坛发帖

