# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150623_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='network',
            name='type',
            field=models.CharField(verbose_name='type', default='W', choices=[('W', 'Wi-Fi'), ('L', 'LTE')], max_length=1),
            preserve_default=False,
        ),
    ]
