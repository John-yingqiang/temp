
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from common.parsers import PlainTextParser
from .permissions import WhiteListOnly
import json
import re

rands_array_path = '/rands/rands_array.json'
rands_map_path = '/rands/rands_map.json'

rands_array = json.loads(open(rands_array_path).read())
rands_map = json.loads(open(rands_map_path).read())


def normal_2_internal(n):
    if n.startswith('+86'):
        n = n[3:]
    if rands_array:
        r = re.match(r'^(1\d{6})(\d{3})(\d)$', n)
        if r:
            return r.group(1) + str(rands_array[int(r.group(2))]).rjust(4, '0') + r.group(3)
    return n


def internal_2_normal(n):
    if rands_map:
        r = re.match(r'^(1\d{6})(\d{4})(\d)$', n)
        if r:
            k = str(int(r.group(2)))
            try:
                return r.group(1) + str(rands_map[k]).rjust(3, '0') + r.group(3)
            except KeyError:
                return n
    return n


class PhoneNumberField(serializers.CharField):

    def to_internal_value(self, data):
        return normal_2_internal(data)


class PhoneTransformView(APIView):

    permission_classes = (WhiteListOnly, )

    parser_classes = (PlainTextParser, )

    def get(self, request, n):
        ret = {
            'normal': internal_2_normal(n),
            'internal': normal_2_internal(n),
        }
        return Response(ret)

    def post(self, request, n):
        text = request.data
        ns = text.split('\n')
        nn = [internal_2_normal(n) for n in ns]
        return Response(nn)
