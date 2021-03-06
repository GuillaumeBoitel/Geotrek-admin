# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-12-03 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0007_create_infra_signa'),
        ('maintenance', '0002_auto_20180608_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name=b'Intervention',
            name='topology',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interventions_set', to='core.Topology', verbose_name='Interventions'),
        ),
        migrations.AlterField(
            model_name=b'Intervention',
            name='topology',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interventions_set', to='core.Topology', verbose_name='Interventions'),
        ),
    ]
