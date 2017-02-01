# -*- coding: utf-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

#from setuptools import find_packages
#from distutils.core import setup
from Cython.Build import cythonize


def process_packages(packages):
    packg = list()
    for pckg in packages:
        p = pckg.replace(".", "/")+"/*.py"
        packg.append(p)
    
    for p in packg:
        print(p)
        
    return packg

packages = process_packages(
            find_packages(exclude=['quantarhei.implementations.*',
                                   'quantarhei.implementations',
                                   'tests.*','tests' ,'docs'])
            )
  
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='quantarhei',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.11.dev3',

    description='Quantarhei: Open Quantum System Theory for Molecular Systems',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/tmancal74/quantarhei',

    # Author details
    author='Tomas Mancal',
    author_email='mancal@karlov.mff.cuni.cz',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='physics, chemistry, quantum mechanics, open quantum systems',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),
 
    ext_modules=cythonize(packages,
                          compiler_directives={'language_level': 3}),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['numpy','scipy','matplotlib'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    ###extras_require={
    ###    'dev': ['check-manifest'],
    ###    'test': ['coverage'],
    ###},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    ###package_data={
    ###    'sample': ['package_data.dat'],
    ###},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    ###data_files=[('my_data', ['data/data_file'])],
    ###

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': ['qrhei=quantarhei.qrhei:main',
                            'lams=quantarhei.lams:main'],
    }
    
)