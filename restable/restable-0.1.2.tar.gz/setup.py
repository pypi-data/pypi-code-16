from setuptools import setup, Extension

DISTNAME = 'restable'
AUTHOR = 'Erick Peirson'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick.peirson@asu.edu'
DESCRIPTION = 'Configuration-driven REST client'
LICENSE = 'GNU GPL 3'
URL = ''
VERSION = '0.1.2'

PACKAGES = ['restable']

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
        "requests>=2.12.1",
        "jsonpickle>=0.9.3",
        "lxml>=3.6.4"
    ]
)
