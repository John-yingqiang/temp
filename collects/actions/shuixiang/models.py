from django.db import models
from datetime import datetime


class SXUser(models.Model):
    """
    水象用户
    """

    user_id = models.IntegerField(unique=True, verbose_name='用户id')
    access_permission = models.BooleanField(default=False, verbose_name="是否准入水象")

    class Meta:
        verbose_name = "水象用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user_id


class IDCard(models.Model):
    """
    身份证信息
    """

    user = models.ForeignKey(SXUser, related_name="id_card")
    name = models.CharField(max_length=5, verbose_name="姓名")
    id = models.CharField(max_length=18, verbose_name="证件号")
    front_file = models.CharField(max_length=100, verbose_name="正面照片地址")
    back_file = models.CharField(max_length=100, verbose_name="反正照片地址")
    nature_file = models.CharField(max_length=100, verbose_name="人脸/手持照")
    nation = models.CharField(max_length=5, verbose_name="民族")
    address = models.CharField(max_length=50, verbose_name="地址")
    issued_by = models.CharField(max_length=20, verbose_name="发证处")
    valid_date = models.CharField(max_length=20, verbose_name="有效期")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "身份证信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class Order(models.Model):
    """
    订单相关
    """

    status_order = (
        (600, "绑卡"),
        (700, "进件"),
        (800, "审核"),
        (900, "签约"),
        (1000, "放款"),
        (1100, "还款")
    )

    status_working = (
        (601, "预绑卡/绑卡成功"),
        (602, "绑卡失败，失败原因其他"),
        (603, "银行卡不合法"),
        (604, "不支持该支付通道的交易"),
        (605, "验证码输入有误"),
        (606, "绑卡确认中"),
        (701, "进件成功"),
        (702, "进件失败"),
        (801, "待审核"),
        (802, "审核中"),
        (803, "审核通过，待签约"),
        (804, "审核拒绝"),
        (901, "签约成功，待放款"),
        (902, "签约失败"),
        (903, "订单状态错误"),
        (904, "用户未绑卡"),
        (1001, "已放款，还款中"),
        (1002, "拒绝"),
        (1101, "已还款（当期）"),
        (1102, "未还款（当期）"),
        (1103, "交易处理中"),
        (1104, "账户余额不足"),
        (1105, "交易失败，请重试")
    )

    user_id = models.IntegerField(db_index=True, verbose_name="用户id")
    no = models.CharField(max_length=20, verbose_name="订单号码")
    status = models.IntegerField(choices=status_order, verbose_name="订单状态")
    status_detail = models.IntegerField(choices=status_working, verbose_name="业务状态")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.no


class BankCard(models.Model):
    """
    银行卡信息
    """

    name = models.CharField(max_length=5, verbose_name="开卡人姓名")
    no = models.CharField(max_length=30, verbose_name="卡号")
    code = models.CharField(max_length=10, verbose_name="编码")
    desc = models.CharField(max_length=10, verbose_name="说明")
    phone = models.CharField(min_length=11, max_length=11, verbose_name="预留手机")
    user = models.ForeignKey(SXUser, related_name="bank_card")

    class Meta:
        verbose_name = "银行卡"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.no
