# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-20 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_auto_20150727_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='/Users/kas/Projects/wordplease/media/'),
        ),
    ]
