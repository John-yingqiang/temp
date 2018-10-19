from rest_framework import serializers


class AuthSerializer(serializers.Serializer):
    auth_name = serializers.CharField(max_length=32)     # identification,number,profile,contacts,gps
    auth_status = serializers.ChoiceField(choices=(1, 10, 11, 13))   # 1,10,11,13
    jie_id = serializers.IntegerField()
