# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0009_auto_20180203_0116'),
    ]

    operations = [
        migrations.AddField(
            model_name='bicycle_type',
            name='level',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle_type',
            name='parent_id',
            field=models.ForeignKey(default=None, blank=True, to='accounting.Bicycle_Type', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle_type',
            name='status',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle_type',
            name='ukr_name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
