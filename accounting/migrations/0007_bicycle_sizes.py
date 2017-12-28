# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0006_remove_bicycle_sizes'),
    ]

    operations = [
        migrations.AddField(
            model_name='bicycle',
            name='sizes',
            field=models.ManyToManyField(to='accounting.FrameSize', blank=True),
            preserve_default=True,
        ),
    ]
