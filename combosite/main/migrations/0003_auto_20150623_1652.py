# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150611_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='dl_speed',
            field=models.FloatField(verbose_name='downlink speed', default=0.0),
        ),
        migrations.AddField(
            model_name='client',
            name='ul_speed',
            field=models.FloatField(verbose_name='uplink speed', default=0.0),
        ),
    ]
