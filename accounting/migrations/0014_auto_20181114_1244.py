# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0013_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='local',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='www',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='type',
            name='ico_status',
            field=models.BooleanField(default=False, verbose_name=b'\xd0\x9d\xd0\xb0\xd1\x8f\xd0\xb2\xd0\xbd\xd1\x96\xd1\x81\xd1\x82\xd1\x8c \xd1\x96\xd0\xba\xd0\xbe\xd0\xbd\xd0\xba\xd0\xb8'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='type',
            name='synonym',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='type',
            name='synonym_ukr',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
