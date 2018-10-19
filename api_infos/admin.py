from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from .models import InsuranceInfoModel
from .insurance_actions import i_heiniu
from datetime import datetime
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter


@admin.register(InsuranceInfoModel)
class InsuranceInfoModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'name', 'identification', 'ip']
    list_max_show_all = 10000
    list_filter = ('i001_status', ('birthday', DateRangeFilter))
    actions = [i_heiniu]
