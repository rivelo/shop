# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2024-01-24 21:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0024_auto_20240122_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogattribute',
            name='created_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name=b'\xd0\x94\xd0\xb0\xd1\x82\xd0\xb0 \xd1\x81\xd1\x82\xd0\xb2\xd0\xbe\xd1\x80\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x8f'),
        ),
        migrations.AlterField(
            model_name='catalogattribute',
            name='updated_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='catalogattributevalue',
            name='updated_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044f'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2024, 1, 27)),
        ),
    ]
