from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import json
from .permissions import WhiteListOnly
from django.core.cache import cache
from .redis_client import rc


@csrf_exempt
def live_check(request, p):
    a = int(p)
    ret = {
        'REMOTE_ADDR': request.META.get('REMOTE_ADDR'),
        'CONTENT_TYPE': request.META.get('CONTENT_TYPE'),
        'method': request.method,
        'body': request.body.decode(),
    }

    try:
        from .__v__ import VERSION
        ret['VERSION'] = VERSION
        ret['OS'] = request.get_os()
        ret['ip'] = request.ip_address
    except:
        pass

    for key in request.META:
        if key.startswith('HTTP'):
            ret[key] = request.META[key]
    return HttpResponse(json.dumps(ret), content_type='application/json')


@login_required
def token_view(request):
    ret = dict(request.token_data)
    return HttpResponse(json.dumps(ret), content_type='application/json')


class TokenView(APIView):
    """
    {"group": "aaa", "tags": ["android", "android8", "xiaomi"]}
    """

    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request):
        return Response(request.token_data)

    def post(self, request):
        request.update_token.update(request.data)
        return Response('OK')


class CacheView(APIView):

    """
    """

    permission_classes = (WhiteListOnly, )

    def get(self, request, key):
        ret = cache.get(key)
        return Response(ret)

    def post(self, request, key):
        data = request.data
        timeout = request.query_params.get('timeout')
        cache.set(key, data, timeout=timeout)
        ret = cache.get(key)
        return Response(ret)
