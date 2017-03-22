import pkg_resources, os, pkgutil
from setuptools import setup, find_packages
from gaet.version import __version__

def read(fname):
    file_ = pkg_resources.resource_filename(__name__, fname)
    with open(file_, 'r') as f:
        return f.read()

setup(
    name                 = 'gaet',
    version              = __version__,
    description          = "Evaluate the quality of a genome assembly based on annotated genes",
    long_description     = read('README.rst'),
    author               = 'Michael Barton',
    author_email         = 'mail@michaelbarton.me.uk',
    install_requires     = read('requirements/default.txt').splitlines(),
    license              = "BSD",
    keywords             = "genomics bioinformatics sequencing assembly",
    url                  = "https://gitlab.com/michaelbarton/gaet/",
    scripts              = ['bin/gaet'],
    packages             = find_packages(),
    package_data         = {'': ['gene_types.yml']},
    include_package_data = True,
    classifiers          = [
        "License :: OSI Approved :: BSD License",
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
)
