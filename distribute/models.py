
from django.db import models
from timeslot.models import TimeSlot, DATETIMEFORMAT
from settings import AUTH_USER_MODEL


class UserSlotBase(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL)
    timeslot = models.ForeignKey(TimeSlot, db_index = True)

    def __unicode__(self):
        return '%s @ %s; %s' % (self.user, self.roster.name, self.timeslot.start.strftime(DATETIMEFORMAT))

    @property
    def roster(self):
        return self.timeslot.roster

    class Meta:
        abstract = True
        unique_together = [['user', 'timeslot', ], ]


class Availability(UserSlotBase):
    pass


class Assignment(UserSlotBase):
    fortrade = models.IntegerField(default = 0)  #todo: dropdown
    giveto = models.ForeignKey(AUTH_USER_MODEL, blank = True, null = True, related_name = 'assignment_gifts')
    note = models.CharField(max_length = 64, default = '')


