from django.contrib import admin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import CollectionsModel
from .actions import c_heiniu, c_zhudaiwang, c_dongfangrongzi


@admin.register(CollectionsModel)
class CollectionsModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'name', 'identification', 'amount', 'period', 'date_joined']
    list_max_show_all = 10000
    list_filter = ('c001_status', 'c002_status', 'c003_status', ('birthday', DateRangeFilter), ('date_joined', DateTimeRangeFilter))
    actions = [c_heiniu, c_zhudaiwang, c_dongfangrongzi]
