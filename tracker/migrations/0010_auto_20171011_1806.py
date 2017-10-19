# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-11 14:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0009_auto_20170912_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='railcars',
            name='bill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='tracker.Bills', verbose_name='платеж'),
        ),
        migrations.AlterField(
            model_name='railcars',
            name='volume',
            field=models.DecimalField(decimal_places=4, help_text='Введите количество топлива в килограммах', max_digits=10, verbose_name='количество по накладной'),
        ),
        migrations.AlterField(
            model_name='tracking',
            name='amount',
            field=models.DecimalField(decimal_places=4, help_text='Введите количество топлива в килограммах', max_digits=10, verbose_name='Количество факт. '),
        ),
    ]