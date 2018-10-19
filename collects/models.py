from django.db import models
from utils.validators import id_validator
from django.utils import timezone


class CollectionsModel(models.Model):
    """
    信息收集
    """

    status_choices = ((0, '未发送'), (1, '发送中'), (2, '发送失败'), (3, '发送成功'))

    date_joined = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    number = models.CharField(max_length=15, unique=True, verbose_name='手机号')
    name = models.CharField(max_length=32, verbose_name='姓名')
    identification = models.CharField(null=True, blank=True, max_length=22, validators=[id_validator], verbose_name='身份证号')  # 检查
    amount = models.IntegerField(null=True, blank=True, verbose_name='万元')
    period = models.IntegerField(null=True, blank=True, verbose_name='月')
    province = models.CharField(null=True, blank=True, max_length=16, verbose_name='省份')
    city = models.CharField(null=True, blank=True, max_length=16, verbose_name='城市')
    marriage = models.CharField(null=True, blank=True, max_length=12, verbose_name='婚姻状况')
    local_account = models.CharField(null=True, blank=True, max_length=4, verbose_name='是否本地户口')
    credit_choice = models.CharField(null=True, blank=True, max_length=8, verbose_name='是否有信用卡')
    job = models.CharField(null=True, blank=True, max_length=8, verbose_name='工作')
    company = models.CharField(null=True, blank=True, max_length=64, verbose_name='公司')
    income_bank = models.IntegerField(default=0, verbose_name='月收入（银行代发工资）')
    income_month = models.IntegerField(default=0, verbose_name='月收入（现金）')
    job_age = models.IntegerField(null=True, blank=True, verbose_name='工龄')
    local_social_security = models.CharField(null=True, blank=True, max_length=64, verbose_name='是否有本地社保')
    local_fund = models.CharField(null=True, blank=True, max_length=64, verbose_name='是否有本地公积金')
    has_house = models.CharField(null=True, blank=True, max_length=64, verbose_name='有房产')
    has_insurance = models.CharField(null=True, blank=True, max_length=64, verbose_name='有保险')
    has_car = models.CharField(null=True, blank=True, max_length=64, verbose_name='有汽车')
    has_creditcard = models.CharField(null=True, blank=True, max_length=64, verbose_name='有信用卡')
    has_car_loan = models.CharField(null=True, blank=True, max_length=64, verbose_name='有车贷')
    has_house_loan = models.CharField(null=True, blank=True, max_length=64, verbose_name='有房贷')
    amount_creditcard = models.IntegerField(null=True, blank=True, verbose_name='信用卡额度（元）')
    amount_weilidai = models.IntegerField(null=True, blank=True, verbose_name='微粒贷额度（元）')
    amount_mayijiebei = models.IntegerField(null=True, blank=True, verbose_name='蚂蚁借呗额度（元）')

    birthday = models.DateTimeField(null=True, blank=True, verbose_name='生日')
    birth = models.CharField(null=True, blank=True, max_length=32, verbose_name='手填生日')
    sex = models.CharField(null=True, blank=True, max_length=32, verbose_name='性别')
    way = models.CharField(null=True, blank=True, max_length=4, verbose_name='上班族_工资发放')
    license = models.CharField(null=True, blank=True, max_length=4, verbose_name='私营业主_营业执照')
    seniority = models.CharField(null=True, blank=True, max_length=4, verbose_name='黑牛工龄')
    salary = models.CharField(null=True,blank=True,max_length=4,verbose_name='月薪')
    user_agent = models.TextField(null=True, blank=True, verbose_name='浏览器信息')

    ip = models.CharField(max_length=32, verbose_name='ip 地址')
    c001_status = models.SmallIntegerField(default=0, choices=status_choices, verbose_name='黑牛贷款')
    c002_status = models.SmallIntegerField(default=0, choices=status_choices, verbose_name='助贷网')
    c003_status = models.SmallIntegerField(default=0, choices=status_choices, verbose_name='东方融资网')
    c004_status = models.SmallIntegerField(default=0, choices=status_choices, verbose_name='龙分期')

    class Meta:
        verbose_name = '收集信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.number

    @property
    def gender(self):
        """
        2：女, 1：男
        :return:
        """
        cert = self.identification
        ret = 2 if int(cert[16]) % 2 is 0 else 1
        return ret
