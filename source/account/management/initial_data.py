
'''
	create initial data for this model, on syncdb
	make sure to check if it doesn't yet exist
'''

from django.contrib.auth import get_user_model


INITIAL_USER = 'mark.verleg@gmail.com'

def initial_data(verbosity, *args, **kwargs):
	'''
		create an admin user
	'''
	if not get_user_model().objects.filter(email = INITIAL_USER):
		get_user_model().objects.create_superuser(email = INITIAL_USER, password = 'admin').save()
		if verbosity:
			print 'created initial user \'%s\' with password \'admin\'; please change the password a.s.a.p.' % INITIAL_USER


