# Created by queenie luc on 01/04/2017
try:
    from setuptools import find_packages
    from distutils.core import setup
except ImportError:
    from distutils.core import setup

__VERSION__ = {}
execfile('cypress_common/version.py', __VERSION__)

config = {
    'description': 'Istuary DeepVision Cypress Common Library',
    'author': 'Istuary DeepVision Team (Cypress)',
    'author_email': "cypress@istuary.com",
    'url': 'https://git.istuary.com/cypress/cypress_common',
    'version': __VERSION__['VERSION'],
    'install_requires': ['redis', 'numpy', 'confluent-kafka', 'kafka-python', 'scipy', 'Pillow'],
    'packages': find_packages(exclude=['docs', 'docker', 'tests']),
    'package_dir': {'cypress_common': 'cypress_common'},
    'scripts': [],
    'license': 'MIT',
    'name': 'cypress_common'
}

setup(**config)
