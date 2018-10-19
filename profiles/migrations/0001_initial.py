# Generated by Django 2.0.3 on 2018-06-25 05:54

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('identification', 'identification'), ('jie_profile', 'jie_profile'), ('number', 'number'), ('bank', 'bank'), ('id_image_in_hand', 'id_image_in_hand')], max_length=16)),
                ('image', models.URLField()),
                ('name', models.CharField(max_length=32)),
                ('desc', models.CharField(max_length=100)),
                ('event_action', jsonfield.fields.JSONField(blank=True, null=True)),
                ('level', models.CharField(choices=[('i', '无效'), ('m', '必备'), ('o', '可选')], max_length=1)),
                ('index', models.IntegerField(db_index=True)),
            ],
            options={
                'ordering': ['index'],
            },
        ),
    ]