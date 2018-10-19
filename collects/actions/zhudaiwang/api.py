def c_zhudaiwang(modeladmin, request, queryset):
    """
    黑牛贷款
    :param modeladmin:
    :param request:
    :param queryset:
    :return:
    """
    print('发送到助贷网', request, queryset)


c_zhudaiwang.short_description = '发送到助贷网'
