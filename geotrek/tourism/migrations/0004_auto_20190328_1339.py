# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2019-03-28 12:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0003_auto_20190306_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristiccontent',
            name='type1',
            field=models.ManyToManyField(blank=True, db_table=b't_r_contenu_touristique_type1', related_name='contents1', to='tourism.TouristicContentType1', verbose_name='Type 1'),
        ),
        migrations.AlterField(
            model_name='touristiccontent',
            name='type2',
            field=models.ManyToManyField(blank=True, db_table=b't_r_contenu_touristique_type2', related_name='contents2', to='tourism.TouristicContentType2', verbose_name='Type 2'),
        ),
    ]
