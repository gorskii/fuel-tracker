# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-02 13:12
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='FuelTypes',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Railcars',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('railcar', models.CharField(max_length=8)),
                ('fuel_brand', models.CharField(max_length=32)),
                ('volume', models.DecimalField(decimal_places=4, max_digits=10)),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tracker.Bills')),
                ('fuel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tracker.FuelTypes')),
            ],
        ),
        migrations.CreateModel(
            name='Tracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=4, max_digits=10)),
                ('comment', models.TextField(default='', max_length=200)),
                ('railcar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tracker.Railcars')),
            ],
        ),
    ]
