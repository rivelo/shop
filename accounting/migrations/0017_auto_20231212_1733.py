# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2023-12-12 17:33
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0016_auto_20181128_0138'),
    ]

    operations = [
#        migrations.AddField(
#            model_name='catalog',
#            name='date',
#            field=models.DateField(blank=True, null=True),
#        ),
#        migrations.AddField(
#            model_name='catalog',
#            name='full_description',
#            field=models.TextField(blank=True, null=True),
#        ),
#        migrations.AddField(
#            model_name='catalog',
#            name='youtube_url',
#            field=models.ManyToManyField(blank=True, to='accounting.YouTube'),
#        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2023, 12, 15)),
        ),
#        migrations.AlterUniqueTogether(
#            name='clientdebts',
#            unique_together=set([('client', 'price', 'cash')]),
#            unique_together=set([('client')]),
#        ),
    ]
