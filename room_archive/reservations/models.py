
from django.db import models
from people.models import Person
from rooms.models import Room
import random
import string


class ActiveReservationManager(models.Manager):
    def get_query_set(self):
        return super(ActiveReservationManager, self).get_query_set().filter(cancelled = None)


class Reservation(models.Model):
    
    name = models.CharField(max_length = 32, blank = True, null = True)
    person = models.ForeignKey(Person, related_name='reservations')
    room = models.ForeignKey(Room, related_name='reservations')
    start = models.DateTimeField()
    end = models.DateTimeField()
    no_show = models.BooleanField(default = False)
    last_modified = models.DateTimeField(auto_now = True)
    delete_code = models.CharField(max_length = 32, blank = True)
    cancelled = models.DateTimeField(null = True, blank = True, default = None)
    
    
    objects = models.Manager()
    active = ActiveReservationManager()
    
    
    class Meta:
        ordering = ['start', 'room']
    
    def save(self):
        if self.pk == None:
            self.delete_code = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(32))
        return super(Reservation, self).save()
    
    def __unicode__(self):
        return '%s' % (self.name or self.person)
    
    @property
    def start_minutes(self):
        return self.start.hour * 60 + self.start.minute
    
    @property
    def end_minutes(self):
        return self.end.hour * 60 + self.end.minute
    
    @property
    def is_cancelled(self):
        return not self.cancelled == None



