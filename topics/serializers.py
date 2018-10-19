from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import Article, Comment, TimeConfig, ReviewBlackList
from utils.time_serializer import convert_to_local_time
from django.core.cache import cache


class CommentSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    # 多级评论

    class Meta:
        model = Comment
        fields = ('id', 'created', 'content', 'nickname')

    def get_created(self, obj):
        return convert_to_local_time(obj.created)


class ArticleNewSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=255)
    art_type = serializers.ChoiceField(choices=(1, 2), required=False)
    loan_amount = serializers.CharField(max_length=32, required=False)
    loan_time = serializers.CharField(max_length=32, required=False)
    loan_contact = serializers.CharField(max_length=32, required=False)

    def __init__(self, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super(self.__class__, self).__init__(**kwargs)

    def validate(self, attrs):
        art_type = attrs.get('art_type')
        if art_type:
            attrs['art_type'] = int(art_type)
        black = ReviewBlackList.objects.get(name='black_number')
        if black:
            user_list = black.black_user
            if int(self.user_id) in user_list:
                raise ValidationError({'msg': black.black_msg})

        if attrs.get('art_type') is 2:
            if attrs.get('loan_amount') is None and attrs.get('loan_contact') is None:
                raise ValidationError({'msg': '参数错误'})

        return attrs


class CommentNewSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField(required=False)
    content = serializers.CharField(max_length=255)


class ArticleSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'created', 'content', 'nickname', 'thumbs', 'art_type', 'loan_amount', 'loan_contact', 'loan_time')

    def get_created(self, obj):
        return convert_to_local_time(obj.created)
