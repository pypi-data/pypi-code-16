"""
Propel

Propel is a package to deploy multiple Python sites/application in virtualenv.

It also allows you to deploy PHP/HTML applications, run scripts and run workers with Supervisor.

For Python application, it uses Virtualenv to isolate each application, Gunicorn+Gevent as the backend server,
Supervisor and Nginx.

For PHP/HTML sites, it just uses the path as it would in normal environment, and you must have php-fpm

"""

import os
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

__about__ = {}
with open(os.path.join(base_dir, "propel", "__about__.py")) as f:
    exec(f.read(), __about__)


setup(
    name=__about__["__title__"],
    version=__about__["__version__"],
    license=__about__["__license__"],
    author=__about__["__author__"],
    author_email=__about__["__email__"],
    description=__about__["__summary__"],
    url=__about__["__uri__"],
    long_description=__doc__,
    py_modules=['propel'],
    entry_points=dict(console_scripts=[
        'propel=propel:cmd',
        'propel-setup=propel:setup_propel']),
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'jinja2',
        'pyyaml==3.11',
        'virtualenvwrapper==4.5.1',
        'supervisor'
    ],
    keywords=['deploy', 'propel', 'flask', 'gunicorn', 'django', 'workers', 'deploy sites', 'deployapp'],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)
