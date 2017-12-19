# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bicycle_Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=200, verbose_name='\u043d\u0430\u0437\u0432\u0430', blank=True)),
                ('image', models.ImageField(upload_to=b'media/upload/bicycle/storage/', verbose_name='\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u043d\u044f')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bicycle_Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model', models.CharField(max_length=255, null=True, blank=True)),
                ('color', models.CharField(max_length=150, null=True, blank=True)),
                ('size', models.CharField(max_length=50, null=True, blank=True)),
                ('service', models.BooleanField(default=False)),
                ('washing', models.BooleanField(default=False)),
                ('serial_number', models.CharField(max_length=50)),
                ('date_in', models.DateField(auto_now_add=True)),
                ('date_out', models.DateField(auto_now_add=True)),
                ('done', models.BooleanField(default=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('price', models.FloatField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('biketype', models.ForeignKey(to='accounting.Bicycle_Type')),
                ('client', models.ForeignKey(to='accounting.Client')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounting.Currency', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage_Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['type'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bicycle_storage',
            name='type',
            field=models.ForeignKey(to='accounting.Storage_Type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle_storage',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle_storage',
            name='wheel_size',
            field=models.ForeignKey(blank=True, to='accounting.Wheel_Size', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle_photo',
            name='bicycle',
            field=models.ForeignKey(verbose_name='\u0430\u043b\u044c\u0431\u043e\u043c', to='accounting.Bicycle_Storage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle_photo',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
