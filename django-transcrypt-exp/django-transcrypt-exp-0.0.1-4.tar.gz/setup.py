# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-transcrypt-exp',
    version='0.0.1-4',
    author=u'Morten B. Rasmussen',
    author_email='mbr@mr-systems.dk',
    packages=[
        'django_transcrypt',
        'django_transcrypt.management',
        'django_transcrypt.management.commands'],
    include_package_data=True,
    url='https://bitbucket.org/cruise/django_transcrypt',
    license='MIT, see LICENSE.txt',
    description='Adds livereload facility together with transcrypt python to' +
                ' javascript transpiling',
    long_description=open('README.txt').read(),
    zip_safe=False,
    install_requires=[
        'django-livereload-server',
        'Transcrypt'],
)
