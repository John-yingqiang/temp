# Generated by Django 2.0.3 on 2018-07-02 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_infos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorInsuranceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, '未发送'), (1, '发送中'), (2, '发送失败'), (3, '发送成功')], default=0, verbose_name='发送状态')),
                ('cid', models.CharField(help_text='i001', max_length=32, verbose_name='渠道标记')),
                ('desc', models.CharField(max_length=64, verbose_name='渠道描述')),
            ],
            options={
                'verbose_name': '保险渠道',
                'verbose_name_plural': '保险渠道',
            },
        ),
        migrations.AddField(
            model_name='insuranceinfomodel',
            name='vendor',
            field=models.ManyToManyField(blank=True, related_name='insurances', to='api_infos.VendorInsuranceModel', verbose_name='保险渠道'),
        ),
    ]