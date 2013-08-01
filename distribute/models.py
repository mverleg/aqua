
from django.db import models
from timeslot.models import TimeSlot, DATETIMEFORMAT
from django.contrib.auth.models import User


class UserSlotBase(models.Model):
    user = models.ForeignKey(User)
    timeslot = models.ForeignKey(TimeSlot, db_index = True)
    
    def __unicode__(self):
        return '%s @ %s; %s' % (self.user, self.roster.name, self.timeslot.start.strftime(DATETIMEFORMAT))
    
    @property
    def roster(self):
        return self.timeslot.roster
    
    class Meta():
        abstract = True
        unique_together = [['user', 'timeslot', ], ]


class Availability(UserSlotBase):
    pass
    

class Assignment(UserSlotBase):
    fortrade = models.IntegerField(default = 0)
    giveto = models.ForeignKey(User, blank = True, null = True, related_name = 'assignment_gifts')
    note = models.CharField(max_length = 64, default = '')
    

