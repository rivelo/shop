# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_auto_20171223_1154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bicycle',
            name='sizes',
        ),
    ]
