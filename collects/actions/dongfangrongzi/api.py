from datetime import datetime
import hashlib
import requests
from common.phone_transform import internal_2_normal, normal_2_internal
from general.celery import app
from django.urls import reverse
import os
from .cities import city_pinyin
from general.events import ServiceEvent


"""
1. 需提供白名单 IP（测试环境 IP,生产环境 IP）
"""


key = 'rongzi.com_8763'
source = 398
url_dong = 'http://mirzr.rongzi.com/rzr/Transfer/Register'

# 测试
# url_dong = 'http://103.242.169.60:19999/rzr/Transfer/Register'
# source = 289


class DongFangRongZiError(Exception):
    def __init__(self, api, error):
        self.api = api
        self.error = error

    def __str__(self):
        return "%s: %s" % (self.api, self.error)


def sign_info(CityName, CellPhoneNumber, RealName, Gender, LoanAmount, TimeStamp):
    """
    Md5 签名格式： CityName+CellPhoneNumber+RealName+Gender+LoanAmount+UtmSource +TimeStamp+密钥
    :return:
    """
    to_sign = CityName + CellPhoneNumber + RealName + str(Gender) + str(LoanAmount) + str(source) + TimeStamp + key
    hash_md5 = hashlib.md5(to_sign.encode('utf-8'))
    sign = hash_md5.hexdigest()
    return sign


def api_send(amount, number, gender, name, city_py, time_str, job_info, income_i, security, creditcard, house, car):
    sign = sign_info(city_py, number, name, gender, amount, time_str)
    data = {
        'LoanAmount': amount,
        'CellPhoneNumber': number,  # 取消混淆
        'Gender': gender,
        'RealName': name,
        'UtmSource': source,
        'CityName': city_py,
        'TimeStamp': time_str,
        'Signature': sign,
        'Identity': job_info,
        'AverageMonthlyIncome': income_i,
        'SocialSecurityFund': security,
        'HaveCreditCard': creditcard,
        'HaveHouse': house,
        'HaveCar': car,
    }
    # print('dongfangdata', data)

    try:
        r = requests.post(url_dong, json=data, timeout=5)
        ret = r.json()
        ServiceEvent(normal_2_internal(number)).ret_dongfangrongzi(ret)
        if ret['Code'] == '0':
            return True
        else:
            return False
    except:
        raise DongFangRongZiError('dongfangrongzi', '东方融资网接口错误')


def task_send(info):
    city_py = ''
    for cp in city_pinyin:
        if cp['city'] == info.city:
            city_py = cp['pinyin']

    if not city_py:
        return

    if info.c003_status not in [0, 2]:
        return

    time_str = datetime.now().strftime('%Y%m%d%H:%M:%S')
    real_number = internal_2_normal(info.number)

    if info.job == '自由职业':
        job_info = 8
    elif info.job == '企业员工':
        job_info = 4
    elif info.job == '个体户':
        job_info = 2
    else:
        return

    income_all = info.income_bank + info.income_month
    if income_all < 4000:
        income_i = 4000
    elif income_all < 5000:
        income_i = 4500
    elif income_all < 10000:
        income_i = 7500
    else:
        income_i = 10000

    if info.local_social_security == '是' and info.local_fund == '是':
        security = 2
    elif info.local_social_security == '是' and info.local_fund == '否':
        security = 4
    elif info.local_social_security == '否' and info.local_fund == '是':
        security = 8
    else:
        security = 1

    if info.has_creditcard == '是':
        creditcard = 1
    else:
        creditcard = 0

    if info.has_house == '有':
        house = 1
    else:
        house = 0

    if info.has_car == '有':
        car = 1
    else:
        car = 0

    info.c003_status = 1
    info.save(update_fields=('c003_status',))
    ret = api_send(amount=info.amount, number=real_number, gender=info.gender, name=info.name,
                   city_py=city_py, time_str=time_str, job_info=job_info, income_i=income_i, security=security,
                   creditcard=creditcard, house=house, car=car)

    if ret:
        info.c003_status = 3
    else:
        info.c003_status = 2
    info.save(update_fields=('c003_status',))
    return info.c003_status


def c_dongfangrongzi(modeladmin, request, queryset):
    """
    黑牛贷款
    c003_status ((0, '未发送'), (1, '发送中'), (2, '发送失败'), (3, '发送成功'))
    :param modeladmin:
    :param request:
    :param queryset:
    :return:
    """
    print('发送到东方融资', request, queryset)
    i_time = 1
    for info in queryset:
        base = os.environ['INTENAL_BASE']
        id = info.id
        url = base + reverse('task_dongfang', args=(id,))
        i_time += 20
        app.send_task('monitors.tasks.url_request', (url,), countdown=i_time)


c_dongfangrongzi.short_description = '发送到东方融资'
