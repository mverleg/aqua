# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Roster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('state', models.IntegerField(default=0, choices=[(0, b'Creating'), (1, b'Entering availabilities'), (2, b'Calculating distribution'), (3, b'Preview distribution (hidden)'), (4, b'Live')])),
            ],
        ),
        migrations.CreateModel(
            name='RosterWorker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extra', models.FloatField(default=0.0)),
                ('roster', models.ForeignKey(to='timeslot.Roster')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField(db_index=True)),
                ('end', models.DateTimeField(db_index=True)),
                ('degeneracy', models.PositiveIntegerField(default=1)),
                ('roster', models.ForeignKey(to='timeslot.Roster')),
            ],
            options={
                'ordering': ['start'],
            },
        ),
    ]
