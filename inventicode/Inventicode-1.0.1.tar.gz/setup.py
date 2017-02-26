# -*- coding: utf-8 -*-
"""Setup file for Inventicode"""
import codecs
import os.path
import re
import sys
from setuptools import setup, find_packages

# avoid a from 'inventicode' import __version__ as version (that compiles inventicode.__init__
#   and is not compatible with bdist_deb)
version = None
for line in codecs.open(os.path.join('inventicode', '__init__.py'), 'r', encoding='utf-8'):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)
python_version = (sys.version_info[0], sys.version_info[1])

# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()

entry_points = {'console_scripts': ['inventicode-django = djangofloor.scripts:django',
                                    'inventicode-aiohttp = djangofloor.scripts:aiohttp']}
try:
    from djangofloor.scripts import set_env
    set_env('inventicode-setup')
except ImportError:
    set_env = None

setup(
    name='Inventicode',
    version=version,
    description='Create labels with QR and barcodes.',
    long_description=long_description,
    license='CeCILL-B',
    url='https://github.com/d9pouces/inventicode',
    entry_points=entry_points,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    author='mgallet',
    author_email='github@19pouces.net',
    install_requires=['djangofloor', 'qrcode', 'pybarcode'],
    classifiers=['Development Status :: 3 - Alpha', 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: Microsoft :: Windows', 'Operating System :: POSIX :: BSD',
                 'Operating System :: POSIX :: Linux', 'Operating System :: Unix',
                 'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
                 'Programming Language :: Python :: 3.4', 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6'],
)
