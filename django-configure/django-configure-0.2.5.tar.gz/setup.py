# coding=utf-8
from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='django-configure',
    version='0.2.5',
    packages=find_packages(),
    url='',
    license='MIT License',
    author='Michał Szostak',
    author_email='szostak.m.f@gmail.com',
    description='Utility for defining external django configs (for end user)',
    install_requires=[
        'dj-database-url>=0.4.2'
    ],
    package_data={
        'django_configure': ['resources/wsgi.py.template'],
    },
    long_description=README,
    keywords = ['configuration', 'django'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        # 'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
