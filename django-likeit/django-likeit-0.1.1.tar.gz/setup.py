#!/usr/bin/env python

from setuptools import setup, find_packages

README = open('README.md').readlines()

setup(
    name='django-likeit',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description=README[2].rstrip('\n'),
    long_description=''.join(README),
    url='https://github.com/malisit/django-likeit',
    download_url='https://github.com/malisit/django-likeit/tarball/0.1',
    author='Muhammed Ali Sit',
    author_email='sitmuhammedali@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    )
