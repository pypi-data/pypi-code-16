from setuptools import setup

VERSION='1.0.3'

setup(
    author='Raul Sampedro',
    author_email='rsrdesarrollo@gmail.com',
    name='lmgtfy-cli',
    version=VERSION,
    url='https://github.com/rsrdesarrollo/lmgtfy-cli/tarball/{}'.format(VERSION),
    license='GPLv3',
    description='Let me Google that for you CLI link generator.',
    scripts=['src/lmgtfy'],
    keywords=['cli', 'google', 'search', 'generator'],
    requires=['clipboard']
)
