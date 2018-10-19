from django.contrib import admin
from .models import *


@admin.register(CreditCoinConfig)
class CreditCoinConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'rank', 'desc', 'icon', 'credit_coin_amount', 'uid']
    ordering = ['-is_active', '-rank']
    list_editable = ('rank', 'is_active')


@admin.register(CouponType)
class CouponTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'rank', 'is_active', 'is_hot', 'is_new_register', 'is_birthday', 'credit_coin',
                    'desc', 'is_phone', 'is_phone_flow', 'phone_amount', 'is_credit_coin', 'credit_coin_amount',
                    'json_detail', 'json_usage']
    ordering = ['-is_active', '-rank', '-is_hot']
    list_editable = ('rank', 'is_active', 'is_hot')
    list_filter = ['is_new_register', 'is_birthday', 'is_phone', 'is_phone_flow', 'is_credit_coin']


@admin.register(CouponBanner)
class CouponBannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'coupon', 'is_active', 'rank']


@admin.register(CouponNews)
class CouponNewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'coupon', 'is_active']


@admin.register(CouponActivity)
class CouponActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'coupon', 'is_active', 'pic', 'rank']
