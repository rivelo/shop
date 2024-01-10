# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2024-01-07 20:12
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0022_auto_20231222_1854'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bicycle_sale',
            options={'ordering': ['-date', 'client', 'model']},
        ),
        migrations.AlterModelOptions(
            name='framesize',
            options={'ordering': ['name', 'inch', 'cm', 'letter']},
        ),
        migrations.AddField(
            model_name='catalog',
            name='barcode',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name=b'barcode other'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='barcode_ean',
            field=models.CharField(blank=True, max_length=13, null=True, verbose_name=b'barcode_eau'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='barcode_upc',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name=b'barcode_upc'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='bike_style',
            field=models.ManyToManyField(blank=True, to='accounting.Bicycle_Type'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='change_history',
            field=models.TextField(blank=True, null=True, verbose_name=b'History of changes on item Catalog '),
        ),
        migrations.AddField(
            model_name='catalog',
            name='manufacture_article',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'manufacture code(article)'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='mistake',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name=b'\xd0\x9f\xd0\xbe\xd0\xbc\xd0\xb8\xd0\xbb\xd0\xba\xd0\xb0 \xd0\xb2 \xd0\xb7\xd0\xb0\xd0\xbf\xd0\xbe\xd0\xb2\xd0\xbd\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x96 \xd0\xba\xd0\xb0\xd1\x80\xd1\x82\xd0\xba\xd0\xb8 \xd1\x82\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x80\xd1\x83'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='mistake_status',
            field=models.BooleanField(default=False, verbose_name=b'\xd0\xa1\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81 \xd0\xbf\xd0\xbe\xd0\xbc\xd0\xb8\xd0\xbb\xd0\xba\xd0\xb8'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='url_web_site',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name=b'\xd0\x9f\xd0\xbe\xd1\x81\xd0\xb8\xd0\xbb\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8f \xd0\xbd\xd0\xb0 \xd0\xbe\xd1\x84\xd1\x96\xd1\x86\xd1\x96\xd0\xb9\xd0\xbd\xd0\xb8\xd0\xb9 \xd1\x81\xd0\xb0\xd0\xb9\xd1\x82'),
        ),
        migrations.AddField(
            model_name='client',
            name='reg_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='reg_shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Shop'),
        ),
        migrations.AddField(
            model_name='client',
            name='reg_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        # migrations.AddField(
            # model_name='clientinvoice',
            # name='shop',
            # field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Shop'),
        # ),
        migrations.AddField(
            model_name='shop',
            name='show',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='full_description',
            field=models.TextField(blank=True, null=True, verbose_name=b'\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81 \xd1\x82\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x80\xd1\x83'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2024, 1, 10)),
        ),
        migrations.AlterField(
            model_name='shopdailysales',
            name='cash',
            field=models.FloatField(verbose_name=b'\xd0\x93\xd0\xbe\xd1\x82\xd1\x96\xd0\xb2\xd0\xba\xd0\xb0'),
        ),
        migrations.AlterField(
            model_name='shopdailysales',
            name='ocash',
            field=models.FloatField(verbose_name=b'\xd0\x92\xd0\xb8\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xbe \xd0\xb7 \xd0\xba\xd0\xb0\xd1\x81\xd0\xb8'),
        ),
        migrations.AlterField(
            model_name='shopdailysales',
            name='tcash',
            field=models.FloatField(verbose_name=b'\xd0\xa2\xd0\xb5\xd1\x80\xd0\xbc\xd1\x96\xd0\xbd\xd0\xb0\xd0\xbb'),
        ),
    ]
