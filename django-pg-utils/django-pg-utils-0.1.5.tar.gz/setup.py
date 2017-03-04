import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requirements = [
]


setup(
    name='django-pg-utils',
    packages=['pg_utils'],
    version='0.1.5',
    description='Utility methods for Django + PostgreSQL applications',
    author='HyperTrack',
    author_email='devops@hypertrack.io',
    url='https://github.com/hypertrack/django-pg-utils',
    license='MIT',
    download_url='https://github.com/hypertrack/django-pg-utils/tarball/0.1',
    keywords=['orm', 'postgres', 'django'],
    classifiers=[],
    install_requires=requirements
)
