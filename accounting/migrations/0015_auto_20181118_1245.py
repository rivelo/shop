# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0014_auto_20181114_1244'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='discount',
            options={'ordering': ['name', 'sale', 'date_start', 'date_end']},
        ),
#        migrations.AddField(
#            model_name='catalog',
#            name='date',
#            field=models.DateField(null=True, blank=True),
#            preserve_default=True,
#        ),
#        migrations.AddField(
#            model_name='catalog',
#            name='full_description',
#            field=models.TextField(null=True, blank=True),
#            preserve_default=True,
#        ),
#        migrations.AddField(
#            model_name='catalog',
#            name='youtube_url',
#            field=models.ManyToManyField(to='accounting.YouTube', null=True, blank=True),
#            preserve_default=True,
#        ),
        migrations.AlterField(
            model_name='bicycle_parts',
            name='catalog',
            field=models.ForeignKey(blank=True, to='accounting.Catalog', null=True),
        ),
        migrations.AlterField(
            model_name='bicycle_parts',
            name='name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='discount',
            name='date_start',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='discount',
            name='manufacture_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='discount',
            name='type_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2018, 11, 21)),
        ),
        migrations.AlterUniqueTogether(
            name='clientdebts',
            unique_together=set([('client', 'date', 'price', 'cash')]),
        ),
    ]
