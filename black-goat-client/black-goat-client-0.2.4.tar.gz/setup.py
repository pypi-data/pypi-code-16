from setuptools import setup, Extension

DISTNAME = 'black-goat-client'
AUTHOR = 'Erick Peirson'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick.peirson@asu.edu'
DESCRIPTION = 'Simple client for the BlackGoat API'
LICENSE = 'GNU GPL 3'
URL = 'http://diging.github.io/black-goat/'
VERSION = '0.2.4'

PACKAGES = ['goat']

setup(
    name=DISTNAME,
    author=AUTHOR,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    version=VERSION,
    packages = PACKAGES,
    include_package_data=True,
    install_requires=[
        "requests>=2.12.1"
    ],
)
