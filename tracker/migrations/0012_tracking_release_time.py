# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-17 11:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0011_auto_20171017_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracking',
            name='release_time',
            field=models.DateTimeField(null=True, verbose_name='отпущен в'),
        ),
    ]
