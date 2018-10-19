from django.db import models
from jsonfield import JSONField
from .jupei_amount import get_amount
from common.mongo import mongo_client, mongodb
from general.settings import MONGO_DB_JIEAPI


class AuthConfig(models.Model):

    type_choinces = [("identification", "identification"), ("jie_profile", "jie_profile"), ("number", "number",),
                     ("bank", "bank",), ("id_image_in_hand", "id_image_in_hand")]

    level_choices = [('i', '无效'), ('m', '必备'), ('o', '可选')]

    type = models.CharField(max_length=16, choices=type_choinces)
    image = models.URLField()
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=100)
    event_action = JSONField(blank=True, null=True)
    level = models.CharField(max_length=1, choices=level_choices)
    index = models.IntegerField(db_index=True)

    class Meta:
        ordering = ['index']


class FeedBack(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    number = models.CharField(max_length=32, verbose_name='手机号')
    device_id = models.CharField(max_length=32, null=True, blank=True, verbose_name='设备id')
    sort = models.CharField(max_length=64, verbose_name='类别')
    content = models.CharField(max_length=10240, verbose_name='内容')

    class Meta:
        verbose_name = "用户反馈"
        verbose_name_plural = "用户反馈"


class JuPei(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    number = models.CharField(max_length=32, null=True, blank=True, verbose_name='手机号')
    user_id = models.IntegerField(unique=True, verbose_name='用户id')
    send_count = models.IntegerField(default=0, verbose_name='申请次数')
    amount = models.IntegerField(default=0, verbose_name='可赔付金额', help_text='单位：分')
    withdraw = models.IntegerField(default=0, verbose_name='已提现金额')

    class Meta:
        verbose_name = "拒就赔"
        verbose_name_plural = verbose_name

    def _check_downloaded(self, product_id):
        r = mongo_client[MONGO_DB_JIEAPI].item_history.find_one({'_id': str(self.user_id)}) or {}
        downloaded = r.get('download', [])
        if not product_id in downloaded:
            return False, '未下载'

        users = mongodb.users.find_one({'_id': self.user_id}) or {}
        applied = users.get('jupei_applied') or []
        if product_id in applied:
            return False, '已申请'

        return True, None

    def update_pei(self, product_id):
        """
        当CP产品数量超过12000个后，用户才可能达到100元
        :return:
        """
        res, msg = self._check_downloaded(product_id)
        if not res:
            return 0, msg

        amount_add = get_amount(self.send_count, self.amount)
        self.amount += amount_add
        self.send_count += 1
        self.save(update_fields=('amount', 'send_count'))
        mongodb.users.update_one({'_id': self.user_id}, {'$addToSet': {'jupei_applied': product_id}}, upsert=True)
        return amount_add, None
