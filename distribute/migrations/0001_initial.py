# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timeslot', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fortrade', models.IntegerField(default=0, choices=[(0, b'(Normal)'), (1, b'Marked for trading'), (2, b'Free to claim'), (3, b'Transfer to someone [giveto]')])),
                ('note', models.CharField(default=b'', max_length=64)),
                ('giveto', models.ForeignKey(related_name='assignment_gifts', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('timeslot', models.ForeignKey(to='timeslot.TimeSlot')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeslot', models.ForeignKey(to='timeslot.TimeSlot')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together=set([('user', 'timeslot')]),
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together=set([('user', 'timeslot')]),
        ),
    ]
