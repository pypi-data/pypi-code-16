from os import path
from setuptools import setup

__version__ = '0.1.4'

SETUP_DIR = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(SETUP_DIR, 'README')) as f:
    long_description = f.read()


# get the dependencies and installs
with open(path.join(SETUP_DIR, 'requirements.txt')) as f:
    all_reqs = f.read().split('\n')


install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]


setup(
    name='trabConfig',
    version=__version__,
    long_description=long_description,
    license='MIT',
    author='Scott Doucet',
    author_email='duroktar@gmail.com',
    description='A simple config parser that supports JSON and YAML',
    packages=['trabconfig'],
    install_requires=install_requires,
    dependency_links=dependency_links
)
