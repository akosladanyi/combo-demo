# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, verbose_name='name', max_length=128)),
                ('mac_address', models.CharField(unique=True, verbose_name='MAC address', max_length=17)),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
            },
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, verbose_name='name', max_length=128)),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
            },
        ),
        migrations.AddField(
            model_name='client',
            name='network',
            field=models.ForeignKey(null=True, blank=True, verbose_name='network', to='main.Network'),
        ),
    ]
