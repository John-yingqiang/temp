from django.db import models
from datetime import datetime
from utils.validators import id_validator


class InsuranceInfoModel(models.Model):
    """
    保险
    """

    status_choices = ((0, '未发送'), (1, '发送中'), (2, '发送失败'), (3, '发送成功'))

    name = models.CharField(max_length=32, verbose_name='姓名')
    number = models.CharField(max_length=15, unique=True, verbose_name='手机号')
    identification = models.CharField(max_length=22, validators=[id_validator], verbose_name='身份证号')
    birthday = models.DateTimeField(null=True, verbose_name='生日')
    ip = models.CharField(max_length=32, verbose_name='ip 地址')
    i001_status = models.SmallIntegerField(default=0, choices=status_choices, verbose_name='黑牛赠险')

    class Meta:
        verbose_name = '保险信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.number


