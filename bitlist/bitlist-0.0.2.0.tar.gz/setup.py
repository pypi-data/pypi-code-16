from distutils.core import setup

setup(
    name             = 'bitlist',
    version          = '0.0.2.0',
    packages         = ['bitlist',],
    install_requires = [],
    license          = 'MIT License',
	url              = 'http://github.com/lapets/bitlist',
	author           = 'A. Lapets',
	author_email     = 'a@lapets.io',
    description      = 'Minimal Python library for working with little-endian list representation of bit strings.',
    long_description = open('README').read(),
)
