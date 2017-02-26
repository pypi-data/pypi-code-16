import os
from setuptools import setup, find_packages

import elemental_core


def _get_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()


name = elemental_core.__title__
version = elemental_core.__version__

description = elemental_core.__summary__
long_description = _get_long_description()
license = elemental_core.__license__
url = elemental_core.__url__

author = elemental_core.__author__
author_email = elemental_core.__email__

classifiers = [
    'Development Status :: 1 - Planning',
    'License :: OSI Approved :: {0}'.format(license),
    'Intended Audience :: Developers',
    'Environment :: Web Environment',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
]
keywords = 'elemental cms core'

packages = find_packages(exclude=('tests', 'docs'))

install_requires = []
extras_require = {
    'test': [
        'pytest'
    ],
    'doc': [
        'sphinx>=1.3.0'
    ]
}

package_data = {}

data_files = []

entry_points = {}


def _run_setup():
    setup_kwargs = {
        'name': name,
        'version': version,
        'description': description,
        'long_description': long_description,
        'url': url,
        'author': author,
        'author_email': author_email,
        'license': license,
        'classifiers': classifiers,
        'keywords': keywords,
        'packages': packages,
        'install_requires': install_requires,
        'extras_require': extras_require,
        'package_data': package_data,
        'data_files': data_files,
        'entry_points': entry_points
    }
    setup(**setup_kwargs)


if __name__ == '__main__':
    _run_setup()
