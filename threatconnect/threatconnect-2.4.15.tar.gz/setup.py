import re
from setuptools import setup, find_packages

with open('threatconnect/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__(?:\s+)?=(?:\s+)?[\'|\"]((?:[0-9]{1,3}(?:\.)?){1,3})[\'|\"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    author='ThreatConnect (support@threatconnect.com)',
    author_email='support@threatconnect.com',
    # convert_2to3_doctests = [''],
    description='Python SDK for ThreatConnect API',
    download_url='https://github.com/ThreatConnect-Inc/threatconnect-python/tarball/{}'.format(version),
    entry_points={
        'console_scripts': [
            'stanchion=bin.stanchion:main'
        ],
    },
    extras_require={
        ':python_version=="2.7"': ['enum34']
    },
    install_requires=[
        'requests==2.13.0',
        'python-dateutil==2.6.0'
    ],
    license = 'Apache License, Version 2',
    name='threatconnect',
    # package_dir = {'': 'src'},
    packages=find_packages(),
    url='https://github.com/ThreatConnect-Inc/threatconnect-python',
    use_2to3=True,
    use_2to3_exclude_fixers=['lib2to3.fixes.fix_print'],
    # use_2to3_fixers = [''],
    version=version
)