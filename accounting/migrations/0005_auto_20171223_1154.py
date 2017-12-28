# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_auto_20171221_0356'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bicycle_Parts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('catalog', models.ForeignKey(to='accounting.Catalog', blank=True)),
                ('type', models.ForeignKey(to='accounting.Type')),
            ],
            options={
                'ordering': ['type'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('name_ukr', models.CharField(max_length=100, null=True, blank=True)),
                ('description_ukr', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bicycle',
            name='bikeparts',
            field=models.ManyToManyField(to='accounting.Bicycle_Parts', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='type',
            name='bike_order',
            field=models.PositiveSmallIntegerField(default=0, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='type',
            name='group',
            field=models.ForeignKey(blank=True, to='accounting.GroupType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2017, 12, 26)),
        ),
    ]
