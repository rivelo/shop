# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0003_auto_20171219_0525'),
    ]

    operations = [
        migrations.CreateModel(
            name='YouTube',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['date', 'description'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bicycle',
            name='country_made',
            field=models.ForeignKey(to='accounting.Country', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle',
            name='geometry',
            field=models.ImageField(max_length=255, null=True, upload_to=b'upload/bicycle/geometry/', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle',
            name='internet',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle',
            name='rating',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle',
            name='warranty',
            field=models.PositiveIntegerField(default=12, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle',
            name='warranty_frame',
            field=models.PositiveIntegerField(default=12),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bicycle',
            name='youtube_url',
            field=models.ManyToManyField(to='accounting.YouTube', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bicycle',
            name='photo',
            field=models.ImageField(max_length=255, null=True, upload_to=b'upload/bicycle/', blank=True),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='logo',
            field=models.ImageField(null=True, upload_to=b'upload/brandlogo/', blank=True),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_end',
            field=models.DateField(default=datetime.date(2017, 12, 24)),
        ),
    ]
