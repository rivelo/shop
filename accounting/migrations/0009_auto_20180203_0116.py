# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0007_bicycle_sizes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bicycle_parts',
            options={'ordering': ['type__bike_order']},
        ),
        migrations.AddField(
            model_name='workticket',
            name='phone_date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='workticket',
            name='phone_user',
            field=models.ForeignKey(related_name=b'p_user', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2018, 2, 6)),
        ),
    ]
