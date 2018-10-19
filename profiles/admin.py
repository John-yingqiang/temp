from django.contrib import admin
from .models import AuthConfig, FeedBack, JuPei


@admin.register(AuthConfig)
class AuthConfigAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'desc', 'level', 'index', 'image']


@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ['created', 'sort', 'content', 'number', 'device_id']
    search_fields = ('number', 'content')


@admin.register(JuPei)
class JuPeiAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'number', 'amount', 'send_count', 'withdraw', 'updated', 'created']
    search_fields = ('number',)
