# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath( path.dirname( __file__ ) )

with open( 'README.md', encoding = "utf-8" ) as f :
    long_description = f.read( )

setup(
    name = 'timetools',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version = '0.6.0',

    description = 'Python utilities relating to synchronization analysis and visualization',
    long_description = long_description,

    # The project's main homepage.
    url = 'https://github.com/blueskyjunkie/timetools',
    download_url = 'https://zenodo.org/search?page=1&size=20&q=timetools',

    # Author details
    author = 'Russell Smiley',
    author_email = 'im.russell.smiley@gmail.com',

    license = 'GPLV3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Hardware',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords = [ 'synchronization', 'visualization', 'analysis', 'PDV', 'MTIE', 'TDEV' ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages = find_packages( exclude = [ 'contrib', 'doc', '*tests*' ] ),
    setup_requires = [
        'setuptools',
        'setuptools-git',
        'wheel',
    ],

    # These will be installed by pip when your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [ 'numpy', 'scipy', 'matplotlib' ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require = {
        'dev' : [ 'zest.releaser[recommended]',
                  'Sphinx',
                  'setuptools',
                  'setuptools-git' ],
        'test' : [ 'nose',
                   'nose-exclude', ],
    },

    zip_safe = False,

)
