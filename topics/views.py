from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ValidationError
from .models import Article, Comment, TimeConfig, PushConfig
from .serializers import ArticleSerializer, CommentSerializer, ArticleNewSerializer, CommentNewSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from general.permissions import IsCustomUser
from common.permissions import WhiteListOnly
from common.redis_client import rc
from general.celery import send_task
from general.settings import INTENAL_BASE
from django.urls import reverse
from profiles.user_info import UserInfoMongo
from utils.invite_code import InviteCode
from datetime import datetime


class ArticlesView(ModelViewSet):
    permission_classes = (IsCustomUser,)

    queryset = Article.objects.filter(status=2)
    serializer_class = ArticleSerializer

    def create(self, request, *args, **kwargs):
        token = request.token_data
        user_id = token['user_id']
        number = token['number']
        serializer = ArticleNewSerializer(data=request.data, user_id=user_id)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        content = data['content']
        art_type = data.get('art_type', 0)
        loan_amount = data.get('loan_amount')
        loan_time = data.get('loan_time')
        loan_contact = data.get('loan_contact')

        create_key = 'topics_views_create' + str(user_id)
        if rc.get(create_key):
            raise ValidationError({'msg': '发帖间隔时间过短，请不要刷屏哦'})

        review_t = TimeConfig.objects.get(name='article')
        rc.set(create_key, 1, review_t.article_gap)

        art_default = {
            'art_type': art_type,
            'loan_amount': loan_amount,
            'loan_time': loan_time,
            'loan_contact': loan_contact,
            'number': number
        }

        art = Article.objects.create(user=user_id, content=content, **art_default)
        thumbed = art.has_thumbed(user_id)
        ret = ArticleSerializer(art).data
        ret['thumbed'] = thumbed
        url = INTENAL_BASE + reverse('review', args=(art.id,))
        send_task('text_review', art.id, content, 'art', url)
        return Response(ret)

    def list(self, request, *args, **kwargs):
        page_num = 25
        page = max(int(request.GET.get('page', 1)), 1)
        art_type = request.GET.get('art_type')
        if art_type:
            self.queryset = self.queryset.filter(art_type=art_type)
        articles = self.queryset[(page-1)*page_num:page*page_num]
        ret = []
        token = request.token_data
        user_id = token['user_id']
        for art in articles:
            has_thumbed = art.has_thumbed(user_id)
            art_data = ArticleSerializer(art).data
            art_data['has_thumbed'] = has_thumbed
            ret.append(art_data)

        user_info = UserInfoMongo(user_id)
        data_ret = {'data': ret}
        data_ret['unread_num'] = user_info.unread_message_nums()
        return Response(data_ret)

    def retrieve(self, request, *args, **kwargs):
        try:
            art = Article.objects.get(id=self.kwargs['pk'])
        except Article.DoesNotExist:
            raise ValidationError({'msg': '对象不存在'})
        token = request.token_data
        user_id = token['user_id']
        has_thumbed = art.has_thumbed(user_id)
        ret = ArticleSerializer(art).data
        ret['has_thumbed'] = has_thumbed

        page_num = 20
        page = max(int(request.GET.get('page', 1)), 1)
        comments = art.a_comments.filter(status=2)[page_num*(page-1):page*page_num]
        data_comments = CommentSerializer(comments, many=True).data
        ret.update({'comments': data_comments})
        return Response(ret)

    @detail_route(methods=['post'], permission_classes=(IsCustomUser,))
    def comment(self, request, pk):
        serializer = CommentNewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        token = request.token_data
        user_id = token['user_id']
        number = token['number']
        content = data['content']

        create_key = 'topics_views_comment' + str(user_id)
        if rc.get(create_key):
            raise ValidationError({'msg': '发帖间隔时间过短，请不要刷屏哦'})

        review_t = TimeConfig.objects.get(name='article')
        rc.set(create_key, 1, review_t.article_gap)

        try:
            art = Article.objects.get(id=pk)
        except Article.DoesNotExist:
            raise ValidationError({'msg': '对象不存在'})
        cmt = None
        comment_id = data.get('comment_id')
        if comment_id:
            try:
                cmt = Comment.objects.get(id=comment_id)
            except Comment.DoesNotExist:
                raise ValidationError({'msg': '对象不存在'})

        comment = Comment.objects.create(user=user_id, content=content, article=art, comment=cmt, number=number)
        url = INTENAL_BASE + reverse('review', args=(comment.id,))
        send_task('text_review', comment.id, content, 'comment', url)
        return Response({'status': 1})

    @detail_route(methods=['post'], permission_classes=(IsCustomUser,))
    def thumb(self, request, pk):
        token = request.token_data
        user_id = token['user_id']
        try:
            art = Article.objects.get(id=pk)
        except Article.DoesNotExist:
            raise ValidationError({'msg': '对象不存在'})

        art.update_thumbs(user_id)
        return Response({'status': 1})

    @list_route(methods=['get'], permission_classes=(IsCustomUser,))
    def topic_messages(self, request):
        token = request.token_data
        user_id = token['user_id']
        messages = UserInfoMongo(user_id).topic_messages
        UserInfoMongo(user_id).read_topic_messages()
        return Response({'messages': messages})

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['partial_update', 'destroy']:  # 暂不支持用户自己删除
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsCustomUser]

        return [permission() for permission in permission_classes]


class ReviewView(APIView):

    permission_classes = (WhiteListOnly,)

    def post(self, request, pk):
        """
        status_choices = ((0, '审核中'), ('1', '审核拒绝'), (2, '审核通过'), (3, '人工审核'))
        spam：0表示非违禁，1表示违禁，2表示建议人工复审
        :param request:
        :param pk:
        :return:
        """
        try:
            data = request.data
            content_type = data['content_type']
            if content_type == 'art':
                art = Article.objects.get(id=pk)
            else:
                art = Comment.objects.get(id=pk)

            spam = data['spam']
            result = data['result']
            if spam == 1:
                art.status = 1
            elif spam == 0:
                # 评论审核通过，push
                art.status = 2
                if content_type == 'comment':
                    push_t = PushConfig.objects.get(name='comment')
                    if push_t.is_push:
                        article = art.article
                        number_push = article.number
                        if number_push:
                            try:
                                content = push_t.content.format(InviteCode().uid_to_code(art.user))
                                send_task('push_notify_to_user', number_push, None, {'text': content})
                                message = {
                                    'art_id': article.id,
                                    'comment_id': art.user,
                                    'comment_user': art.user,
                                    'read': False,
                                    'content': content,
                                    'time': datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                                }
                                UserInfoMongo(article.user).add_topic_messages(message)
                                UserInfoMongo(article.user).update_unread_topic_message()
                            except:
                                raise Exception('es,number获取device_info', '接口调用失败,手机号：%s' % number_push)

            else:
                art.status = 3
            art.review_msg = str(result)[:250]
            art.save(update_fields=['status', 'review_msg'])
        except Article.DoesNotExist:
            raise ValidationError({'msg': '对象不存在'})

        return Response({'status': 1})




