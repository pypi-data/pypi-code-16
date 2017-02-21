# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215_
import multiprocessing
assert multiprocessing
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'ambition-django-cachebuster',
    description = 'Django 1.3, Python 2.7/3.5 ready cache busting app',
    long_description=read('README.rst'),
    author='James Addison',
    author_email='code@scottisheyes.com',
    packages = ['cachebuster','cachebuster.templatetags','cachebuster.detectors'],
    version = '0.3',
    url='http://github.com/ambitioninc/django-cachebuster',
    keywords=[],
    license='BSD',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Topic :: Internet :: WWW/HTTP :: WSGI',
      'Framework :: Django',
    ],
)