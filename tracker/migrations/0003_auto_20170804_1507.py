# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-04 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_auto_20170804_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracking',
            name='comment',
            field=models.TextField(blank=True, default='', max_length=200),
        ),
    ]
