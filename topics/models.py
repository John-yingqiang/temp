from django.db import models
from django.utils.functional import cached_property
from utils.invite_code import InviteCode
import django.utils.timezone as timezone
from common.mongo import mongodb
from common.model_cache import CachedModel
from jsonfield import JSONField


class Article(models.Model):

    status_choices = ((0, '审核中'), (1, '审核拒绝'), (2, '审核通过'), (3, '人工审核'))
    art_type_choices = ((0, ''), (1, '出借'), (2, '求借'))

    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    user = models.IntegerField(db_index=True, verbose_name='用户id')
    number = models.CharField(max_length=32, null=True, blank=True, verbose_name='用户手机号')
    content = models.CharField(max_length=255, verbose_name='内容')
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name='审核状态')
    review_msg = models.CharField(max_length=255, null=True, blank=True, verbose_name='审核意见')
    art_type = models.SmallIntegerField(choices=art_type_choices, db_index=True, default=0, verbose_name='出/求借')
    loan_amount = models.CharField(max_length=255, null=True, blank=True, verbose_name='借款金额')
    loan_time = models.CharField(max_length=255, null=True, blank=True, verbose_name='借款期限')
    loan_contact = models.CharField(max_length=255, null=True, blank=True, verbose_name='联系方式')

    class Meta:
        ordering = ['-created']
        verbose_name = '主题'
        verbose_name_plural = verbose_name

    @property
    def nickname(self):
        name = InviteCode().uid_to_code(self.user)
        return '匿名用户' + name

    @property
    def thumbs(self):
        thumb_history = mongodb.topics_info.find_one({'_id': self.id}, projection={'topic_thumbs': True, '_id': False}) or {}
        return len(thumb_history.get('topic_thumbs', []))

    def has_thumbed(self, user_id):
        thumb_history = mongodb.topics_info.find_one({'_id': self.id}, projection={'topic_thumbs': True, '_id': False}) or {}
        return user_id in thumb_history.get('topic_thumbs', [])

    def update_thumbs(self, user_id):
        mongodb.topics_info.update_one({'_id': self.id}, {'$addToSet': {'topic_thumbs': user_id}}, upsert=True)


class Comment(models.Model):

    status_choices = ((0, '审核中'), (1, '审核拒绝'), (2, '审核通过'), (3, '人工审核'))
    comment_type_choices = ((0, '评论一个主题'), (1, '评论一条评论'))

    created = models.DateTimeField(auto_now_add=True)
    user = models.IntegerField(db_index=True, verbose_name='用户id')
    number = models.CharField(max_length=32, null=True, blank=True, verbose_name='用户手机号')
    content = models.CharField(max_length=255, verbose_name='内容')
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name='审核状态')
    review_msg = models.CharField(max_length=255, null=True, blank=True, verbose_name='审核意见')
    article = models.ForeignKey(Article, related_name='a_comments', null=True, blank=True, on_delete=models.CASCADE, verbose_name='主题id')
    comment = models.ForeignKey('self', related_name='c_comments', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父级评论')
    comment_type = models.SmallIntegerField(choices=comment_type_choices, default=0, verbose_name='评论类型')

    class Meta:
        ordering = ['-created']
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    @property
    def nickname(self):
        name = InviteCode().uid_to_code(self.user)
        return '匿名用户' + name


class TimeConfig(CachedModel):
    CACHE_KEY = 'name'

    name = models.CharField(max_length=16, verbose_name='标记', help_text='不可以更改')
    desc = models.CharField(max_length=64, verbose_name='描述')
    article_gap = models.PositiveIntegerField(verbose_name='发帖间隔时间', help_text='单位:秒')
    article_same = models.PositiveIntegerField(verbose_name='发重复内容间隔时间', help_text='单位:秒')
    article_same_rate = models.SmallIntegerField(verbose_name='内容相似度', null=True, blank=True, help_text='百分比：90')

    class Meta:
        verbose_name = '审核配置'
        verbose_name_plural = verbose_name


class PushConfig(CachedModel):
    CACHE_KEY = 'name'

    name = models.CharField(max_length=16, unique=True, verbose_name='标记', help_text='不可以更改')
    is_push = models.BooleanField(verbose_name='是否推送', default=True)
    content = models.CharField(max_length=128, verbose_name='推送内容')

    class Meta:
        verbose_name = '推送配置'
        verbose_name_plural = verbose_name


class ReviewBlackList(CachedModel):
    CACHE_KEY = 'name'

    name = models.CharField(max_length=16, unique=True, verbose_name='标记')
    black_user = JSONField(null=True, blank=True, default=[], verbose_name='用户id黑名单')
    black_msg = models.CharField(max_length=64, null=True, blank=True, verbose_name='原因')

    class Meta:
        verbose_name = '审核黑名单'
        verbose_name_plural = verbose_name


"""
class TimeLine(models.Model):
    
    备用，用户时间轴
    
    created = models.DateTimeField(verbose_name='创建时间')
    user = models.IntegerField(db_index=True, verbose_name='用户id')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    is_own = models.BooleanField(verbose_name='是否是自己的')

    class Meta:
        ordering = ['-created']
        verbose_name = '时间轴'
        verbose_name_plural = verbose_name
"""
