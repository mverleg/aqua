# -*- coding: utf-8 -*-

'''
    for installing with pip
'''

from distutils.core import setup
from setuptools import find_packages

setup(
    name='PROJNAME',
    version='0.0.1',
    author=u'Mark V',
    author_email='noreply.mail.nl',
    packages=find_packages(),
    include_package_data=True,
    url='git+https://bitbucket.org/mverleg/PROJNAME',
    license='revised BSD license; see LICENSE.txt',
    description='see README.srt',
    zip_safe=True,
    install_requires = [
    	'django',
    ],
)


