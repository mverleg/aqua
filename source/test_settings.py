# Test server Django settings for aqua project.

from settings import *
from os.path import join, exists
from os import chmod


DBPATH = join(BASE_DIR, '..', 'writable', 'test.db')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DBPATH,
    }
}

if exists(DBPATH):
	chmod(DBPATH, 0770)

print '\n***USING TEST SETTINGS***\n'



