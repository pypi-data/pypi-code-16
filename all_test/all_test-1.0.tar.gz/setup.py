#!/usr/bin/env python
from setuptools import setup

setup(
    name='all_test',
    version='1.0',
    py_modules=['all_test', 'delPyc'],
    packages=['basic', 'public'],
    author = 'Me',
    author_email = 'me@example.com',
    description = 'This is all_test Package',
    entry_points = {  
        'console_scripts': [  
            'xxxtest = all_test.all_test:main'  
        ]  
    }
)
