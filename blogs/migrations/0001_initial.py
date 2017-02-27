# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(default=b'', max_length=250, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.OneToOneField(related_name='blog', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('name', models.CharField(max_length=250, serialize=False, primary_key=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('intro', models.TextField(max_length=250)),
                ('body', models.TextField()),
                ('image_url', models.URLField(null=True, blank=True)),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('blog', models.ForeignKey(related_name='posts', to='blogs.Blog')),
                ('categories', models.ManyToManyField(related_name='posts', to='blogs.Category')),
            ],
        ),
    ]
