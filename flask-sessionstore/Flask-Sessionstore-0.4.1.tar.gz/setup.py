"""
Flask-Session
-------------

Flask-Session is an extension for Flask that adds support for 
Server-side Session to your application.

"""
from setuptools import setup
from flask_sessionstore import __version__

setup(
    name='Flask-Sessionstore',
    version=__version__,
    url='https://github.com/mcrowson/flask-sessionstore',
    license='BSD',
    author='Matthew Crowson',
    author_email='matthew.d.crowson@gmail.com',
    description='Adds session support to your Flask application',
    long_description=__doc__,
    packages=['flask_sessionstore'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8'
    ],
    test_suite='test_session',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
