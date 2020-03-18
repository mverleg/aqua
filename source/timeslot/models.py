
from django.db import models
from datetime import date, timedelta
from settings import AUTH_USER_MODEL

DATEFORMAT = '%Y-%m-%d'
TIMEFORMAT = '%H:%M'
DATETIMEFORMAT = '%s %s' % (DATEFORMAT, TIMEFORMAT)


class Roster(models.Model):
    name = models.CharField(max_length = 32, unique = True)
    start = models.DateField()
    end = models.DateField()
    state = models.IntegerField(default = 0, choices = (
        (0, 'Creating'),
        (1, 'Entering availabilities'),
        (2, 'Calculating distribution'),
        (3, 'Preview distribution (hidden)'),
        (4, 'Live'),
    ))

    def __unicode__(self):
        return self.name

    ''' Total time occupied by timeslots (so not counting degeneracy) '''
    @property
    def total_duration(self):
        return reduce(lambda d1, d2: d1 + d2, map(lambda ts: ts.duration, TimeSlot.objects.filter(roster = self)))

    ''' Total time for all workers combined (so counting extra for degenerate slots) '''
    @property
    def total_work_time(self):
        roster_timeslots = TimeSlot.objects.filter(roster = self)
        if roster_timeslots:
            return reduce(lambda duration1, duration2: duration1 + duration2, map(lambda timeslot: timeslot.duration * timeslot.degeneracy, roster_timeslots))
        else:
            return timedelta(seconds = 0)

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

    @property
    def active_around_now(self):
        day = timedelta(days = 1)
        if self.start < date.today() + 7 * day and self.end > date.today():
            return True
        return False


class TimeSlot(models.Model):
    roster = models.ForeignKey(Roster)
    start = models.DateTimeField(db_index = True)
    end = models.DateTimeField(db_index = True)
    degeneracy = models.PositiveIntegerField(default = 1)
    #pay_percentage = models.PositiveIntegerField(default = 100)
    #user = models.ForeignKey(User, blank = True, null = True)
    holiday = models.BooleanField(default=False)

    class Meta:
        ordering = ['start', ]

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

    #@property
    #def ppercentage(self):
    #    return self.pay_percentage

    def year(self):
        return self.start.year

    def week(self):
        return self.start.isocalendar()[1]


class RosterWorker(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL)
    roster = models.ForeignKey(Roster)
    extra = models.FloatField(default = 0.0)

    def __unicode__(self):
        return '%s @ %s' % (self.user, self.roster.name)
