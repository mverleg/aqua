
from django.db import models
import random
import string


class Person(models.Model):
    
    email = models.EmailField(unique = True)
    name = models.CharField(max_length = 32, null = True)
    email_token = models.CharField(max_length = 32, blank = True)
    confirmations = models.BooleanField(default = True)
    
    def save(self):
        if self.pk == None:
            self.email_token = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(32))
        return super(Person, self).save()
    
    def __unicode__(self):
        return '%s' % self.name or 'n/a'

    @property
    def no_shows(self):
        from reservations.models import Reservation
        return Reservation.objects.filter(person = self, no_show = True)
