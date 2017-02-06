"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

PROJECT_NAME = 'BestSignAPI'

here = path.abspath(path.dirname(__file__))

exec(compile(open(path.join(here, 'src', PROJECT_NAME, 'version.py')).read(), path.join(here, 'src', PROJECT_NAME, 'version.py'), 'exec'))

# Get the long description from the relevant file
#with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    #long_description = f.read()

setup(
    name=PROJECT_NAME,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION,

    description='Python library for BestSign API',
    #long_description=long_description,

    # The project's main homepage.
    url='https://www.bestsign.cn',

    # Author details
    author='BestSign Test Team',
    author_email='allqa@bestsign.cn',

    # Choose your license
    license='Apache License, Version 2.0',

    # What does your project relate to?
    keywords='robot auto automation API',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    package_dir={'': 'src'},
    packages=['BestSignAPI'],
    #packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        # 'dpath',
        'pycrypto',
        'requests'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    ## have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)
