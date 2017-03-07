import os
from setuptools import setup, find_packages

setup(
    name     = 'file-resubmit',
    version  = '0.1.0',
    packages = find_packages(),
    requires = ['python (>= 3.3)', 'django (>= 1.8)'],
    description  = 'Keeps submited files when validation errors occur.',
    author       = 'Ilya Shalyapin',
    author_email = 'ishalyapin@gmail.com',
    license      = 'MIT License',
    keywords     = 'django form filefield resubmit',
    classifiers  = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.5',
    ],
)
