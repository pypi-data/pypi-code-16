from os import path
from setuptools import setup, find_packages
from bgtemplates import __version__


directory = path.dirname(path.abspath(__file__))
with open(path.join(directory, 'requirements.txt')) as f:
    required = f.read().splitlines()

setup(
    name='bgtemplates',
    version=__version__,
    author='Barcelona Biomedical Genomics Lab',
    author_email='bbglab@irbbarcelona.org',
    license='Apache 2.0',
    url='https://bitbucket.org/bgframework/bgtemplates',
    packages=find_packages(exclude=['bgtemplates.templates.*.mypackage']),  #  exclude from setup the packages that are not used by the this project directly. However, they are finally include in the manifest
    install_requires=required,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bgtemplates = bgtemplates.bgtemplates:cli',
        ]
    }
)
