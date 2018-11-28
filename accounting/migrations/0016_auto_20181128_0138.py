# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0015_auto_20181118_1245'),
    ]
    operations = [
        migrations.AddField(
            model_name='dealer',
            name='color',
            field=models.CharField(max_length=30, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dealer',
            name='street',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dealermanager',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dealermanager',
            name='email',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dealermanager',
            name='phone',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2018, 12, 1)),
        ),
#        migrations.AlterUniqueTogether(
#            name='clientdebts',
#            unique_together=set([('client', 'date', 'price', 'cash', 'description')]),
#        ),
    ]
