# Django settings for aqua project.

# No final slash
SITE_BASE_URL = 'http://www.aqua.markv.nl/'
LOGIN_URL = '/login/'

# Additional locations of static files
#STATICFILES_DIRS = (
#    '/live/aqua/static',
#)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.messages',
    #'django.contrib.staticfiles',
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

DEBUG = True
ALLOWED_HOSTS = ['.aqua.markv.nl', ]

from socket import gethostname
if gethostname() in ['mulan', 'genie', 'rafiki',]:
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '.aqua.db',
        }
    }
elif gethostname() in ['bambi', 'ursula']:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'aqua',                       # Or path to database file if using sqlite3.
            'USER': 'aqua',                       # Not used with sqlite3.
            'PASSWORD': 'wcq6MELmdASKBSuqP',      # Not used with sqlite3.
            'HOST': '127.0.0.1',                  # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',                       # Set to empty string for default. Not used with sqlite3.
        }
    }
    DEBUG = False
else:
    raise Exception('hostname not known, no database settings')
if DEBUG:
    INSTALLED_APPS += ('django.contrib.staticfiles', )
    STATICFILES_DIRS = ('/home/mark/aqua/static', )
#DEBUG = True # tmp

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'reserveringenstudielandschap@gmail.com'
EMAIL_HOST_PASSWORD = 'zaalwachten'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

PREPEND_WWW = False
APPEND_SLASH = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
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
#STATIC_ROOT = '/web/aqua/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'abc#2uxr=+c*u%pt(*zdckg1s9=uk1ab2%c1e*)z9u7b06*j0r'

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

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

