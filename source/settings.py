
'''
	specific settings for your project;
	always extend existing lists
'''

from mu3.settings import *
from local import *
from os import path


BASE_DIR = path.dirname(path.dirname(__file__))

''' path of the site-wide base template, which should contain a {% block content %} '''
BASE_TEMPLATE = 'base.html'
BASE_EMAIL_TEMPLATE = 'base_email.html'

AUTH_USER_MODEL = 'account.MyUser'

INSTALLED_APPS += (
	'base',
	'account',
	'reactables',
	'statix',
	
	'django.contrib.admin',
)

MEDIA_ROOT = path.join(BASE_DIR, 'data')
STATIC_ROOT = path.join(BASE_DIR, 'static')

STATIX_URL = '/'

TEMPLATE_CONTEXT_PROCESSORS += (
	'base.context.context_settings.context_settings',
	'base.context.javascript_settings.javascript_settings',
)

STATICFILES_DIRS += (
	path.join(BASE_DIR, 'dev/bower'),
)

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'mdilligaf'
EMAIL_HOST_PASSWORD = 'froink42'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


