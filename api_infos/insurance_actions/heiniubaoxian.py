from Crypto.Cipher import DES
import base64
# from pyDes import des, ECB, PAD_PKCS5
import pyDes
from general.settings import INTENAL_BASE
from django.urls import reverse
from general.celery import app
import hashlib
from common.phone_transform import internal_2_normal
import requests
from general.events import ServiceEvent


channel = 'jieqiankuaishou'
subchannel = 'jqksapi1'
secret_key = '766422b8'
url = 'https://www.heiniubao.com/insurance/enhanced'
# 测试
# url = 'http://47.92.104.74:9099/insurance/enhanced'


def des_data(data):
    method = pyDes.des(secret_key, pyDes.ECB, None, pad=None, padmode=pyDes.PAD_PKCS5)
    k = method.encrypt(data.encode('utf-8'))
    return base64.b64encode(k).decode()


def md5_sign(info):
    real_number = internal_2_normal(info.number)
    to_sign = info.identification + info.name + real_number + channel + "baoxian-$@"
    hash_md5 = hashlib.md5(to_sign.encode('utf-8'))
    sign = hash_md5.hexdigest()
    return sign


class HeiNiuError(Exception):
    def __init__(self, api, error):
        self.api = api
        self.error = error

    def __str__(self):
        return "%s: %s" % (self.api, self.error)


def task_send(info):
    """

    :param info:
    :return:
    """
    if info.i001_status not in [0, 2]:
        return

    sign = md5_sign(info)
    real_number = internal_2_normal(info.number)
    data = {
        'name': des_data(info.name),
        'phone': des_data(real_number),
        'channel': channel,
        'subchannel': subchannel,
        'customer_ip': info.ip,
        'sign': sign,
        'id_no': des_data(info.identification)
    }
    try:
        r = requests.get(url, data, timeout=5)
        ret = r.json()
        # print('rr', ret)
        ServiceEvent(info.number).ret_heiniu(ret)
        if ret['error_code'] is '0':
            info.i001_status = 3
        else:
            info.i001_status = 2
        info.save(update_fields=('i001_status',))
        # print('ret i', info.i001_status)
        return info.i001_status

    except:
        raise HeiNiuError('heiniu', '黑牛接口错误')


def i_heiniu(modeladmin, request, queryset):
    """
    黑牛赠险
    :param modeladmin:
    :param request:
    :param queryset:
    :return:
    """
    # PKCS5Padding
    print('发送到黑牛赠险', request, queryset)
    i_time = 1
    for info in queryset:
        id = info.id
        i_time += 20
        url = INTENAL_BASE + reverse('task_heiniu', args=(id,))
        app.send_task('monitors.tasks.url_request', (url,), countdown=i_time)


i_heiniu.short_description = '发送到黑牛赠险'
