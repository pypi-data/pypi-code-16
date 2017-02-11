# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='tornado_mail',
    author='ruitian',
    author_email='ike960705@gmail.com',
    description='A email plugin for tornado. It is a fake Flask_mail.',
    url='https://github.com/ruitian/tornado_mail.git',
    version='0.2.0',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    package_data = {
        '': ['*.py']
    },
    install_requires=[
        'tornado>=4.0.0'
    ]
)
