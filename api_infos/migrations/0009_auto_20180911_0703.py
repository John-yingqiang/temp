# Generated by Django 2.0.3 on 2018-09-10 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_infos', '0008_delete_collectionsmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insuranceinfomodel',
            name='number',
            field=models.CharField(max_length=15, unique=True, verbose_name='手机号'),
        ),
    ]
