from os import path
from setuptools import setup


__version__ = '0.1.0'

SETUP_DIR = path.abspath(path.dirname(__file__))


# Get the long description from the README file.
with open(path.join(SETUP_DIR, 'README.rst')) as f:
    long_description = f.read()


# get the dependencies and installs
with open(path.join(SETUP_DIR, 'requirements.txt')) as f:
    all_reqs = f.read().split('\n')


install_requires = [x.strip() for x in all_reqs if 'git+' not in x]


setup(
    name='trabBuild',
    version=__version__,
    packages=['trabbuild'],
    license='Apache Software License',
    author='Scott Doucet',
    author_email='duroktar@gmail.com',
    description='A script for updating and building python dists',
    long_description=long_description,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'trabbuild = trabbuild.__main__'
        ]
    }
)
