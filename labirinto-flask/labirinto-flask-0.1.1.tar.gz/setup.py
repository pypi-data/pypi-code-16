# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.rst', 'r') as readme_file:
    README = readme_file.read()

setup(
    name='labirinto-flask',
    version='0.1.1',
    author='gilzoide',
    author_email='gilzoide@gmail.com',
    description='Joguinho de labirinto usando Flask + GTM',
    long_description=README,
    url='https://github.com/gilzoide/labirinto-flask',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Development Status :: 3 - Alpha',
    ],
    install_requires=['flask',
                      'flask-mongoengine',
                      'PyYAML',
                      'Flask-Security',
                      'Flask-Bootstrap',
                      'Flask-Admin'],
    packages=['labirinto']
)
