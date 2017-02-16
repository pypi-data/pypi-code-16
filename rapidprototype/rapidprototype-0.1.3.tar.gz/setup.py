#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
import os
from setuptools import setup, find_packages

import rapidprototype


def readme():
    try:
        os.system('pandoc --from=markdown --to=rst README.md -o README.rst')
        with open('README.rst') as f:
            return f.read()
    except:
        return '''**Django rapidprototype** A django application to help
        designers to create rapid prototyping for projects.'''


install_requires = [
    'django>=1.9.1',
    'pillow>=3.1.0'
]



setup(
    name='rapidprototype',
    url='https://github.com/minrock/django_rapidprototype',
    download_url='https://github.com/minrock/django_rapidprototype/tarball/%s/' % rapidprototype.__version__,
    author="minrock",
    author_email='lmoncarisg@gmail.com',
    keywords='Django prototype html',
    description='Library for create easy prototypes with django',
    license='BSD',
    long_description=readme(),
    classifiers=[
      'Framework :: Django',
      'Topic :: Utilities'
    ],
    version=rapidprototype.__version__,
    install_requires=install_requires,
    package_dir={'': '.'},
    packages=find_packages('.', exclude=['tests', '*.tests', 'docs', 'example', 'media']),
)