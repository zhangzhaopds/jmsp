# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-10 01:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=100)),
                ('user_psw', models.CharField(max_length=100)),
                ('user_email', models.EmailField(max_length=254)),
            ],
        ),
    ]