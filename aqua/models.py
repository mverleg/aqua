
from django.contrib.auth.models import User, AbstractBaseUser, UserManager,\
    AbstractUser
from django.db import models

"""
'''
    custom user, with birthday field
'''
class AquaUser(AbstractUser):
    birthday = models.DateField(blank = True, default = None)
    
    def __unicode__(self):
        return self.get_full_name()
    
    class Meta:
        db_table = 'auth_user'
"""
