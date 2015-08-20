# Django settings for aqua project.

# No final slash
from os.path import exists, join, realpath, dirname
from os.path import join
from random import SystemRandom
import string

BASE_DIR = dirname(realpath(__file__))

SITE_BASE_URL = 'http://www.aqua.markv.nl'
LOGIN_URL = '/login/'

# Additional locations of static files
#STATICFILES_DIRS = (
#    '/live/aqua/static',
#)

# this url is bound to a specific account
BIG_ROOM_URL = 'http://persoonlijkrooster.ru.nl/ical?54d15a18&eu=dTg3NzE2MA==&t=82bc7bd6-4049-479c-8659-ae85dda5be02&zoneFeed=true'

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	#'django.contrib.sites',
	#'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	#'extra',
	#'booking',
	#'rooms',
	#'reservations',
	#'people',
	#'moderate',
	#'colorfield',
	'aqua',
	#'working',
	'timeslot',
	'distribute',
	'finalroster',
	#'general',
)

AUTH_USER_MODEL = 'aqua.AquaUser'
#AUTH_USER_MODEL = 'auth.User'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'reserveringenstudielandschap@gmail.com'
EMAIL_HOST_PASSWORD = 'zaalwachten'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

PREPEND_WWW = False
APPEND_SLASH = True

ADMINS = (
	# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
	'django.core.context_processors.request',
	'aqua.context.context_settings.context_settings',
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False ## TODO this should be true

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = join(BASE_DIR, 'static/')

#STATICFILES_DIRS = [join(BASE_DIR, 'aqua', 'static')]

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# http://ianalexandr.com/blog/getting-started-with-django-logging-in-5-minutes.html
LOG_FILE = join(BASE_DIR, '..', 'logs', 'error.django.log') if exists(join(BASE_DIR, '..', 'logs')) else 'error.log'
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
			'datefmt' : "%d/%b/%Y %H:%M:%S"
		},
		'simple': {
			'format': '%(levelname)s %(message)s'
		},
	},
	'handlers': {
		'file': {
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': LOG_FILE,
			'formatter': 'verbose'
		},
	},
	'loggers': {
		'django': {
			'handlers':['file'],
			'propagate': True,
			'level':'INFO',
		},
	}
}

try:
	if not exists(join(BASE_DIR, 'local.py')):
		with open(join(BASE_DIR, 'local.py'), 'w+') as fh:
			fh.write('"""\nLocal (machine specific) settings that overwrite the general ones.\n"""\n\n')
			fh.write('BASE_DIR = dirname(realpath(__file__))')
			fh.write('DATABASES = {\'default\': {\n\t\'ENGINE\': \'django.db.backends.sqlite3\',\n\t\'NAME\': \'aqua.db\',\n}}\n\n')
			fh.write('ALLOWED_HOSTS = [\'localhost\', \'http://.localhost.markv.nl\',]\n\n')
			fh.write('SECRET_KEY = "{0:s}"\n\n'.format(''.join(SystemRandom().choice(string.letters + string.digits + '#$%&()*+,-./:;?@[]^_`{|}~') for _ in range(50))))
			fh.write('TEMPLATE_DEBUG = DEBUG = False\n\n')
			fh.write('# use this to put notifications on the main page\nSITEWIDE_NOTIFICATION = \'\'\n\n\n')
except Exception:
	print 'could not create local.py settings file'

from local import *



