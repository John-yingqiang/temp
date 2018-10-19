from rest_framework.exceptions import ValidationError


def verify_identification(s):
    """
    验证身份证号码是否有效
    :param s: 身份证号码字符串
    :return:
    """
    if len(s) != 18:
        return False
    last = sum(map(lambda x: int(x[0]) * x[1], zip(s[0:17], [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]))) % 11
    verified_array = [1, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    if s[17] == 'X' or s[17] == 'x':
        return last == 2
    else:
        return int(s[17]) == verified_array[last]


def id_validator(s):
    if not verify_identification(s):
        raise ValidationError('not a valid id number.')


class RaiseMessage(object):

    def __init__(self, msg=None):
        if msg:
            raise ValidationError({'msg': msg})

    def user_not_exist(self):
        raise ValidationError({'msg': '用户不存在'})

    def user_exist(self):
        raise ValidationError({'msg': '用户已存在'})

    def phone_password(self):
        raise ValidationError({'msg': '手机号或密码错误'})

    def auth_not(self):
        raise ValidationError({'msg': '没有权限'})

    def obj_not_exist(self):
        raise ValidationError({'msg': '对象不存在'})

    def id_verified(self):
        raise ValidationError({'msg': '身份已认证'})

    def credit_level_fail(self):
        raise ValidationError({'msg': '信用等级不够'})

    def has_signed(self):
        raise ValidationError({'msg': '今日已签到'})

    def credit_coin_fail(self):
        raise ValidationError({'msg': '信用币不够'})

    def credit_coin_overlimit(self):
        raise ValidationError({'msg': '信用币数量太大'})

    def credit_coin_case(self):
        raise ValidationError({'msg': '信用币参数错误'})

    def coupon_not_start(self):
        raise ValidationError({'msg': '活动未开始'})

    def coupon_need_credit_level(self):
        raise ValidationError({'msg': '信用等级不够，快去提高信用吧'})

    def coupon_need_coin(self):
        raise ValidationError({'msg': '信用币不足，去获取更多信用币吧'})

    def coupon_is_expire(self):
        raise ValidationError({'msg': '信用券已失效'})

    def coupon_status_error(self):
        raise ValidationError({'msg': '红包状态错误'})
