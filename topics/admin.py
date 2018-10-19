from django.contrib import admin
from .models import Article, Comment, TimeConfig, ReviewBlackList, PushConfig


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'user', 'content', 'status', 'review_msg']
    ordering = ['-id']
    list_filter = ('status',)
    list_editable = ('content', 'status')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'user', 'content', 'article', 'status', 'review_msg']
    ordering = ['-id']
    list_filter = ('status',)
    list_editable = ('content', 'status')


@admin.register(TimeConfig)
class TimeConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'desc', 'article_gap', 'article_same', 'article_same_rate']
    ordering = ['-id']
    list_editable = ('article_gap', 'article_same', 'article_same_rate')


@admin.register(ReviewBlackList)
class ReviewBlackListAdmin(admin.ModelAdmin):
    list_display = ['id', 'black_user']
    list_editable = ('black_user',)


@admin.register(PushConfig)
class PushConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'content', 'is_push']
