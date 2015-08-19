"""
Local (machine specific) settings that overwrite the general ones.
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'aqua',
        'USER': 'aqua_user',
        'PASSWORD': 'giethiedeijah',
        'HOST': 'mysql-aqua.science.ru.nl',
        'PORT': '3306',
    }
}

ALLOWED_HOSTS = ['www.aqua.science.ru.nl', 'aqua.science.ru.nl', 'localhost',]

#DATABASES = {
#	'default': {
#		'ENGINE': 'django.db.backends.sqlite3',
#		'NAME': 'aqua.db',
#	}
#}



