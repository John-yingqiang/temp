from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import InsuranceInfoModel
from profiles.permissions import IsCustomUser
from general.permissions import WhiteListOnly
import requests
from general.settings import API_BASE_USER
from rest_framework.exceptions import ValidationError
from .models import InsuranceInfoModel
from .insurance_actions.heiniubaoxian import task_send
from datetime import datetime
from django.utils import timezone
from general.settings import TIME_ZONE
import pytz


class InsuranceInfoView(APIView):
    """
    # 用户同意保险、贷款协议，数据用来和第三方对接
    在实名认证后，调用，不填信息时，默认使用身份证、姓名、手机号信息
    """
    permission_classes = (IsCustomUser,)

    def post(self, request):
        # add other user info
        # url_info = BASE_HOST + '/api/tasks/user_info'
        url_info = API_BASE_USER
        # 实名认证成功后，内网api 获取用户信息
        token_data = request.token_data
        user_id = token_data['user_id']
        user_number = token_data['number']
        params_to = {'user_id': user_id, 'number': user_number}
        r = requests.post(url_info, params_to, timeout=5)
        user_info = r.json()  # {'name': '', 'identification':''}

        identification = user_info['identification']
        birthday = datetime(year=int(identification[6:10]), month=int(identification[10:12]), day=int(identification[12:14]))
        in_default = {
            'name': user_info['name'],
            'identification': identification,
            'ip': request.ip_address,
            'birthday': timezone.make_aware(birthday, timezone=pytz.timezone(TIME_ZONE), is_dst=False)
        }

        insurance, created = InsuranceInfoModel.objects.get_or_create(number=user_number, defaults=in_default)
        return Response({'status': created})


class TaskHeiNiuView(APIView):

    permission_classes = (WhiteListOnly,)

    def get(self, request, id):
        info = InsuranceInfoModel.objects.get(id=id)
        ret = task_send(info)
        return Response({'msg': None})
