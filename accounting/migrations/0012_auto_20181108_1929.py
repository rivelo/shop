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
            model_name='worktype',
            name='block',
            field=models.BooleanField(default=False, verbose_name=b'\xd0\x91\xd0\xbb\xd0\xbe\xd0\xba/\xd0\xbe\xd0\xb1\xd1\x94\xd0\xb4\xd0\xbd\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8f \xd1\x80\xd0\xbe\xd0\xb1\xd1\x96\xd1\x82'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='worktype',
            name='component_type',
            field=models.ManyToManyField(to='accounting.Type', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='worktype',
            name='dependence_work',
            field=models.ManyToManyField(related_name='dependence_work_rel_+', to='accounting.WorkType', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='worktype',
            name='disable',
            field=models.BooleanField(default=False, verbose_name=b'\xd0\x92\xd1\x96\xd0\xb4\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x8f'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='worktype',
            name='plus',
            field=models.BooleanField(default=False, verbose_name=b'\xd0\xa1\xd1\x83\xd0\xbc\xd0\xb0+'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='worktype',
            name='sale',
            field=models.FloatField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='costs',
            name='cost_type',
            field=models.ForeignKey(related_name=b'costs', default=3, to='accounting.CostType'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2018, 11, 11)),
        ),
    ]
