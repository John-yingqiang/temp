import hashlib
import requests
from common.phone_transform import internal_2_normal, normal_2_internal
from general.events import ServiceEvent
import os
from django.urls import reverse
from general.celery import app
from datetime import datetime

# 测试
url_testheiniu = 'http://47.92.104.74:9099/loan/collector'
testchannel = 'test'
testkey = 'heiniuloan-$@'
#正式
url_heiniu = 'https://www.heiniubao.com/loan/collector'
channel = 'jqks01'
key = '2c01758d-f7c8-48db-be56-22cda7041993'


class HeiNiuError(Exception):
    def __init__(self, api, error):
        self.api = api
        self.error = error

    def __str__(self):
        return "%s: %s" % (self.api, self.error)


def sign_info(name, phone, channel):
    """
    Md5 签名格式： name + phone + channel + 密钥
    :return:
    """
    to_sign = name + phone + channel + key
    hash_md5 = hashlib.md5(to_sign.encode('utf-8'))
    sign = hash_md5.hexdigest()
    return sign



def api_send(name, mobile, sex, birth, credit, amount, policy, weilidai, house, car, occupation, salary, experience, way, fund, license, customer_ip):
    sign = sign_info(name, mobile, channel)
    data = {
        'name': name,
        'mobile': mobile,
        'sex': sex,
        'birth': birth,
        'credit': credit,
        'amount': amount,
        'policy': policy,
        'weilidai': weilidai,
        'house': house,
        'car': car,
        'occupation': occupation,
        'salary': salary,
        'channel': channel,
        'customer_ip': customer_ip,
        'sign': sign
    }
    #上班族不填营业执照
    if occupation == 'A':
        data['experience'] = experience
        data['way'] = way
        data['fund'] = fund
    #公务员不填营业执照、工资发放和公积金
    elif occupation =='B':
        data['experience'] = experience
    #私营业主不填工作时间、工资发放和公积金
    elif occupation == 'C':
        data['license'] = license
    try:
        r = requests.post(url_heiniu, data, timeout=5)
        ret = r.json()
        # print(ret)
        ServiceEvent(normal_2_internal(mobile)).ret_heiniu(ret)

        if ret['error_code'] == 0:
            return True
        else:
            return False
    except:
        raise HeiNiuError('heiniu', '黑牛网接口错误')

def handle_jsondata(data):
    if data.c001_status not in [0, 2]:
        return
    real_number = internal_2_normal(data.number)
    if data.amount_weilidai == 0:
        weilidai = 'N'
    else:
        weilidai = 'Y'

    data.c001_status = 1
    data.save(update_fields=('c001_status',))
    ret = api_send(name=data.name, mobile=real_number, sex=data.sex, birth=data.birth,
                   credit=data.credit_choice,amount=data.amount, policy=data.has_insurance,
                   weilidai=weilidai,house=data.has_house, car=data.has_car, occupation=data.job,
                   salary=data.salary,experience=data.seniority, way=data.way,
                   fund=data.local_fund, license=data.license,customer_ip=data.ip)
    if ret:
        data.c001_status = 3
    else:
        data.c001_status = 2
    data.save(update_fields=('c001_status',))
    return ret

def c_heiniu(modeladmin, request, queryset):
    """
    黑牛贷款
    :param modeladmin:
    :param request:
    :param queryset:
    :return:
    """
    print('发送到黑牛贷款', request, queryset)

    i_time = 1
    for info in queryset:
        base = os.environ['INTENAL_BASE']
        id = info.id
        url = base + reverse('task_heiniu', args=(id,))
        i_time += 20
        app.send_task('monitors.tasks.url_request', (url,), countdown=i_time)
        # request.get(url)

c_heiniu.short_description = '发送到黑牛贷款'
