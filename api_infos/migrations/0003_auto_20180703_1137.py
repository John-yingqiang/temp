# Generated by Django 2.0.3 on 2018-07-03 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_infos', '0002_auto_20180702_2106'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='insuranceinfomodel',
            name='vendor',
        ),
        migrations.AddField(
            model_name='insuranceinfomodel',
            name='i001_status',
            field=models.SmallIntegerField(choices=[(0, '未发送'), (1, '发送中'), (2, '发送失败'), (3, '发送成功')], default=0, verbose_name='黑牛赠险'),
        ),
        migrations.DeleteModel(
            name='VendorInsuranceModel',
        ),
    ]
