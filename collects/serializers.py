from rest_framework import serializers
from .models import CollectionsModel
from utils.validators import id_validator


class CollectionsModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = CollectionsModel
        fields = ('number', 'amount', 'period', 'name', 'identification', 'province', 'city', 'marriage',
                  'local_account', 'credit_choice', 'job', 'company', 'income_bank', 'income_month', 'job_age',
                  'local_social_security', 'local_fund', 'amount_weilidai', 'amount_mayijiebei', 'has_house',
                  'has_insurance', 'has_car', 'has_creditcard', 'has_car_loan', 'has_house_loan', 'amount_creditcard',
                  'sex', 'birth', 'salary', 'seniority', 'license', 'way', 'user_agent')


class InterNumberSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=32)
    identification = serializers.CharField(max_length=22, validators=[id_validator])
    amount = serializers.IntegerField()
    period = serializers.IntegerField()
