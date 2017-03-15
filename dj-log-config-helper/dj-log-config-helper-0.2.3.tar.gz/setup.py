# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

install_requires = ['django']

setup(
    name='dj-log-config-helper',
    version='0.2.3',
    url='https://github.com/Harvard-University-iCommons/dj-log-config-helper',
    author='Jaime Bermudez',
    author_email='jaime_bermudez@harvard.edu',
    description='Simplify log configuration across Django projects',
    long_description=readme,
    include_package_data=True,
    license=license,
    zip_safe=False,
    py_modules=['dj_log_config_helper'],
    platforms=['any'],
    install_requires=install_requires,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
