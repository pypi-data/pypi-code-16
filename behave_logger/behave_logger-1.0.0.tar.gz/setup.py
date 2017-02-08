from setuptools import setup

VERSION = '1.0.0'

setup(
    name='behave_logger',
    packages=['behave_logger'],
    version=VERSION,
    description='A specific logger util for Behave',
    author='Martin Borba',
    author_email='borbamartin@gmail.com',
    url='https://github.com/borbamartin/behave-logger',
    download_url='https://github.com/borbamartin/behave-logger/tarball/{}'.format(VERSION),
    keywords=['testing', 'logging', 'behave', 'python'],
    classifiers=[],
)
