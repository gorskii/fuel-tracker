# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 07:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_auto_20170824_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='bills',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Сумма'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bills',
            name='bill',
            field=models.CharField(max_length=32, verbose_name='Платёж'),
        ),
        migrations.AlterField(
            model_name='bills',
            name='supplier',
            field=models.CharField(default='', max_length=32, verbose_name='Поставщик'),
        ),
    ]
