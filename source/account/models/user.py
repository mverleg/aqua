
from django.db import models
from muuser.models.user import MuUser
from muuser.models.address import MuAddress, AddressMixin


#class Address(MuAddress):
#	class Meta: abstract = False


class MyUser(MuUser, AddressMixin):
	
	#address = models.ForeignKey(Address, blank = True, null = True)
	
	class Meta:
		app_label = 'account'
		verbose_name = 'user'
		verbose_name_plural = 'users'


