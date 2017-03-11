#!/usr/bin/env python3
from distutils.core import setup


setup(
    name='wizards',
    version='1.2.0',
    description='Wizards of Industry Common Library',
    author='Cochise Ruhulessin',
    author_email='cochiseruhulessin@gmail.com',
    url='https://www.wizardsofindustry.net',
    install_requires=[
        'werkzeug',
        'marshmallow'
    ],
    packages=[
        'wizards',
        'wizards.wsgi'
    ]
)
