
from django.db import models
from django.contrib.auth.models import User

DATEFORMAT = '%Y-%m-%d'
TIMEFORMAT = '%H:%M'
DATETIMEFORMAT = '%s %s' % (DATEFORMAT, TIMEFORMAT)


class Roster(models.Model):
    name = models.CharField(max_length = 32, unique = True)
    start = models.DateField()
    end = models.DateField()
    state = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return self.name
    
    @property
    def total_duration(self):
        return reduce(lambda d1, d2: d1 + d2, map(lambda ts: ts.duration, TimeSlot.objects.filter(roster = self))) 
    
    @property
    def total_timeslots(self):
        return TimeSlot.objects.filter(roster = self.pk).count()
    
    @property
    def total_users(self):
        return RosterWorker.objects.filter(roster = self).count()
    
    def users(self):
        return map(lambda rw: rw.user, RosterWorker.objects.filter(roster = self))
    
    @property
    def timestr(self):
        return '%s tot %s' % (self.start.strftime(DATEFORMAT), self.end.strftime(DATEFORMAT))
    

class TimeSlot(models.Model):
    roster = models.ForeignKey(Roster)
    start = models.DateTimeField(db_index = True)
    end = models.DateTimeField(db_index = True)
    degeneracy = models.PositiveIntegerField(default = 1)
    #user = models.ForeignKey(User, blank = True, null = True)
    
    def __unicode__(self):
        return '%s-%s' % (self.start.strftime(DATETIMEFORMAT), self.end.strftime(TIMEFORMAT))
    
    @property
    def start_minutes(self):
        return self.start.hour * 60 + self.start.minute
    
    @property
    def end_minutes(self):
        return self.end.hour * 60 + self.end.minute
    
    @property
    def duration(self):
        return self.end - self.start
    
    @property
    def assignments(self):
        from distribute.models import Assignment
        return Assignment.objects.filter(timeslot = self)
    
    @property
    def timestr(self):
        return '%s van %s tot %s' % (self.start.strftime(DATEFORMAT), self.end.strftime(TIMEFORMAT), self.end.strftime(TIMEFORMAT))
    
    def year(self):
        return self.start.year
    
    def week(self):
        return self.start.isocalendar()[1]
    

class RosterWorker(models.Model):
    user = models.ForeignKey(User)
    roster = models.ForeignKey(Roster)
    extra = models.FloatField(default = 0.0)
    
    def __unicode__(self):
        return '%s @ %s' % (self.user, self.roster.name)
    


   
