from .redis_client import rc
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import WhiteListOnly
from .encoders import MongoJsonEncoder
import json

log_name = "logcount"


def add_log_count(key):
    rc.hincrby(log_name, key, 1)


class RedisView(APIView):

    """
    """

    permission_classes = (WhiteListOnly, )

    def get(self, request, name=log_name):
        key = request.query_params.get('k')
        if key:
            ret = rc.hget(name, key)
        else:
            ret = rc.hgetall(name)

        if isinstance(ret, dict):
            ret = dict([(k.decode(), v.decode()) for k, v in ret.items()])
        return Response(ret)

    def post(self, request, name=log_name):
        data = request.data
        rc.hmset(name, data)
        return Response('OK')

    def delete(self, request, name=log_name):
        key = request.query_params.get('key')
        if key:
            rc.hdel(name, key)
        return Response('OK')
