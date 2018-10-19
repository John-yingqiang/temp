from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AuthSerializer
from general.permissions import WhiteListOnly
from profiles.user_info import UserInfoMongo
from profiles.credit_level import CreditCoin


# 来自 base
class AuthView(APIView):
    """
    认证状态更新后，jie 更新信用币奖励
    """
    permission_classes = (WhiteListOnly,)

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        auth_name = data['auth_name']
        auth_status = data['auth_status']
        jie_id = data['jie_id']
        user_info = UserInfoMongo(jie_id)
        user_info.update_auth({auth_name: auth_status})
        CreditCoin(user_info).add_auth_coin(auth_name, auth_status)
        return Response({})


# class IdentificationView(APIView):
#     """
#     认证状态更新后，jie 更新 身份证号码
#     """
#     permission_classes = (WhiteListOnly,)
#
#     def post(self, request):
#         serializer = AuthSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data
#         auth_name = data['auth_name']
#         auth_status = data['auth_status']
#         jie_id = data['jie_id']
#         user_info = UserInfoMongo(jie_id)
#
#         CreditCoin(user_info).add_auth_coin(auth_name, auth_status)
#         return Response({})
