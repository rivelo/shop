# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2024-01-22 16:33
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0023_auto_20240107_2012'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043d\u044f')),
                ('updated_date', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044f')),
                ('type', models.ManyToManyField(blank=True, to='accounting.Type')),
                ('updated_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['pk', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CatalogAttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('value_float', models.FloatField(blank=True, null=True)),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043d\u044f')),
                ('updated_date', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044f')),
                ('attr_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.CatalogAttribute')),
                ('updated_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['attr_id', 'value', 'value_float'],
            },
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['pk', 'name'],
            },
        ),
        migrations.AddField(
            model_name='catalog',
            name='created_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='catalog',
            name='created_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='barcode_ean',
            field=models.CharField(blank=True, max_length=13, null=True, verbose_name=b'barcode_EAN'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='count',
            field=models.IntegerField(verbose_name='\u041a\u0456\u043b\u044c\u043a\u0456\u0441\u0442\u044c \u0432 \u043c\u0430\u0433\u0430\u0437\u0438\u043d\u0430\u0445'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Country', verbose_name=b'\xd0\x9a\xd1\x80\xd0\xb0\xd1\x97\xd0\xbd\xd0\xb0 \xd0\xb2\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb1\xd0\xbd\xd0\xb8\xd0\xba'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='date',
            field=models.DateField(blank=True, null=True, verbose_name='\u0421\u0442\u0440\u043e\u043a \u043f\u0440\u0438\u0434\u0430\u0442\u043d\u043e\u0441\u0442\u0456'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='\u041f\u0440\u0438\u043c\u0456\u0442\u043a\u0438 \u0434\u043b\u044f \u0441\u0435\u0431\u0435'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='full_description',
            field=models.TextField(blank=True, null=True, verbose_name='\u041e\u043f\u0438\u0441 \u0442\u043e\u0432\u0430\u0440\u0443 \u0434\u043b\u044f Web-\u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='length',
            field=models.FloatField(blank=True, null=True, verbose_name='\u0414\u043e\u0432\u0436\u0438\u043d\u0430 (\u0434\u043b\u044f \u0442\u043e\u0432\u0430\u0440\u0456\u0432 \u044f\u043a\u0456 \u043f\u0440\u043e\u0434\u0430\u044e\u0442\u044c\u0441\u044f \u043d\u0430 \u043c\u0435\u0442\u0440\u0438)'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='show',
            field=models.BooleanField(default=False, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441 \u0432\u0456\u0434\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u043d\u044f'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='user_update',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='year',
            field=models.IntegerField(blank=True, null=True, verbose_name='\u041c\u043e\u0434\u0435\u043b\u044c\u043d\u0438\u0439 \u0440\u0456\u043a'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2024, 1, 25)),
        ),
        migrations.AddField(
            model_name='catalog',
            name='attributes',
            field=models.ManyToManyField(blank=True, to='accounting.CatalogAttributeValue'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='season',
            field=models.ManyToManyField(blank=True, to='accounting.Season'),
        ),
    ]