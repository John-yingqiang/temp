from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from .serializers import CollectionsModelSerializer, InterNumberSerializer
from django.shortcuts import HttpResponse
from .models import CollectionsModel
from datetime import datetime
from common.permissions import WhiteListOnly
from .actions.dongfangrongzi.api import task_send
from django.utils import timezone
from general.settings import TIME_ZONE, API_MOBILE_HIT
import pytz
from .actions.heiniudai.api import handle_jsondata
import os
from django.urls import reverse
from general.celery import app
from django.forms import model_to_dict
from collects.actions.longfenqi.api import send_long_fen_qi
import requests
from general.permissions import IsCustomUser
from common.phone_transform import normal_2_internal, internal_2_normal
from common.logs import add_log_count
import traceback


class CollectModelView(APIView):
    """
    信息收集
    """

    def post(self, request):
        # 注意对外的h5页面手机号要混淆再保存
        serializer = CollectionsModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        number = data.pop('number')
        identification = data['identification']
        birthday = datetime(year=int(identification[6:10]), month=int(identification[10:12]), day=int(identification[12:14]))
        birthday = timezone.make_aware(birthday, timezone=pytz.timezone(TIME_ZONE), is_dst=False)
        data.update({'birthday': birthday, 'ip': request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')})
        created = None

        if not CollectionsModel.objects.filter(number=number).exists():
            collect, created = CollectionsModel.objects.get_or_create(number=number, defaults=data)
        return Response({'status': created})


class HNCollectModeView(APIView):
    def post(self, request):
        # 注意对外的h5页面手机号要混淆再保存
        serializer = CollectionsModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        #不能 pop   number 还要用
        number = data.get('number')
        data['ip'] = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
        data.update({'ip': request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')})
        created = None

        if not CollectionsModel.objects.filter(number=number).exists():
            collect, created = CollectionsModel.objects.get_or_create(number=number, defaults=data)

            #数据实时发送
            # handle_jsondata(data)
            base = os.environ['INTENAL_BASE']
            id = collect.id
            url = base + reverse('task_heiniu', args=(id,))
            app.send_task('monitors.tasks.url_request', (url,))

        return Response({'status': created})


class TaskDongFangView(APIView):
    """
    东方融资异步发送任务
    """
    permission_classes = (WhiteListOnly,)

    def get(self, request, id):
        info = CollectionsModel.objects.get(id=id)
        ret = task_send(info)
        if not ret:
            info.c003_status = 2
            info.save(update_fields=['c003_status'])
        return Response({'msg': None})


class TaskHeiNiuView(APIView):
    """
    黑牛异步发送任务
    """
    permission_classes = (WhiteListOnly,)

    def get(self, request, id):
        data = CollectionsModel.objects.get(id=id)
        ret = handle_jsondata(data)
        if not ret:
            data.c001_status = 2
            data.save(update_fields=['c001_status'])
        return Response({'msg': None})


class LongFenQiView(APIView):
    permission_classes = (IsCustomUser,)

    def post(self, request):
        serializer = InterNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        token = request.token_data
        number = token['number']
        cm, created = CollectionsModel.objects.get_or_create(number=number, defaults=data)
        url = API_MOBILE_HIT.format('hit_longfq', number)
        data['number'] = number
        r = requests.get(url, data)
        hit = r.json()['hit']
        ret = {'review': False}  # False 未通过审核
        if not hit:
            try:
                res = send_long_fen_qi(internal_2_normal(number), data['name'], data['identification'], str(data['amount']), str(data['period']))
                os = request.get_os()
                # print('res', res)
                if os == 'ios':
                    ret['url'] = res.get('ios')
                else:
                    ret['url'] = res.get('android')
                ret['review'] = True if ret['url'] else False
                cm.c004_status = 3
                cm.save(update_fields=['c004_status'])
            except:
                add_log_count('jiemisc_collects_longfenqi_send')
                traceback.print_exc()
                cm.c004_status = 2
                cm.save(update_fields=['c004_status'])
                raise ValidationError({'msg': '服务器暂时不可用，请稍后重试'})

        return Response(ret)
