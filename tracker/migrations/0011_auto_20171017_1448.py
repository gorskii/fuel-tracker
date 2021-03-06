# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-17 10:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0010_auto_20171011_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='railcars',
            name='is_released',
            field=models.BooleanField(default=False, verbose_name='отпущен'),
        ),
        migrations.AlterField(
            model_name='bills',
            name='bill',
            field=models.CharField(max_length=32, unique=True, verbose_name='Номер сделки'),
        ),
        migrations.AlterField(
            model_name='bills',
            name='bill_date',
            field=models.DateField(default=django.utils.timezone.localdate, verbose_name='Дата сделки'),
        ),
        migrations.AlterField(
            model_name='railcars',
            name='bill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='tracker.Bills', verbose_name='номер сделки'),
        ),
    ]
