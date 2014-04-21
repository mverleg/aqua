
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.sites.models import Site
from django.db import models


'''
    custom user, with birthday field
'''
class AquaUser(AbstractUser):
    
    birthday = models.DateField(null = True, blank = True, default = None)
    
    objects = UserManager()
    
    def __unicode__(self):
        return self.get_full_name() or self.username
    
    class Meta:
        db_table = 'auth_user'


