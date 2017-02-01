#!/usr/bin/env python
"""An extension to add supprt for SQLAlchemy to Hypr."""


from setuptools import setup, find_packages

PROJECT = 'hypr_sqlalchemy'
VERSION = '0.2.1'


try:
    long_description = open('README', 'rt').read()
except IOError:
    long_description = ''


setup(

    name=PROJECT,
    version=VERSION,

    description=__doc__,
    long_description=long_description,

    author='Morgan Delahaye-Prat',
    author_email='mdp@sillog.net',

    url='https://project-hypr.github.io/sqlalchemy',

    install_requires=open('requirements.txt').read().splitlines(),
    tests_require=open('requirements_test.txt').read().splitlines(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=[],

    namespace_packages=['hypr'],
    entry_points={
        'hypr.models': [
            'SqlAlchemyModel = hypr.sqlalchemy:SqlAlchemyModel',
        ]
    },

    license='BSD',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]

)
