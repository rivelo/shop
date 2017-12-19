# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20171101_1233'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bicycle_photo',
            options={'ordering': ['bicycle']},
        ),
        migrations.AlterModelOptions(
            name='bicycle_storage',
            options={'ordering': ['client']},
        ),
        migrations.AlterField(
            model_name='bicycle_photo',
            name='image',
            field=models.ImageField(upload_to=b'upload/bicycle/storage/', verbose_name='\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u043d\u044f'),
        ),
        migrations.AlterField(
            model_name='bicycle_storage',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='photo',
            field=models.FileField(null=True, upload_to=b'upload/catalog/%Y/', blank=True),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2017, 12, 22)),
        ),
    ]
