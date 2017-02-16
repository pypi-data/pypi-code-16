from setuptools import setup

setup(
    name             = 'dml',
    version          = '0.0.16.0',
    packages         = ['dml',],
    install_requires = ['pymongo',],
    license          = 'MIT License',
	url              = 'http://datamechanics.org',
	author           = 'Andrei Lapets',
	author_email     = 'a@lapets.io',
    description      = 'Common functionalities for building Data Mechanics platform components.',
    long_description = open('README').read(),
)
