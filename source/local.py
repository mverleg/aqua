
'''
    a few local, potentially secret, settings
    do not include this in your repository!
'''

from mu3.settings import DATABASES  # @UnresolvedImport
from os import path

BASE_DIR = path.dirname(path.dirname(__file__))

SITE_URL = 'markv.nl'

SECRET_KEY = '^i%bu)5uyt@_*qh3jglew(-k6kd9gwvmabj3fto_f3(er5*s%y'

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': path.join(BASE_DIR, 'data/default.sqlite3'),
}

SITE_URL = 'markv.nl'

ALLOWED_HOSTS = ['.%s' % SITE_URL]

DEBUG = True


