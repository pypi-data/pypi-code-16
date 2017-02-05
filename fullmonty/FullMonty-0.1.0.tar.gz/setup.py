# from distutils.core import setup
import os
import re
from setuptools import setup

import sys

if sys.version_info < (2, 6):
    print('FullMonty requires python 2.6 or newer')
    exit(-1)


VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


# noinspection PyArgumentEqualDefault
def get_project_version():
    """
    Get the version from __init__.py with a line: /^__version__\s*=\s*(\S+)/
    If it doesn't exist try to load it from the VERSION.txt file.
    If still no joy, then return '0.0.0'

    :returns: the version string
    :rtype: str
    """

    # trying __init__.py first
    try:
        file_name = os.path.join(os.getcwd(), 'fullmonty', '__init__.py')
        # noinspection PyBroadException
        try:
            with open(file_name, 'r', encoding='utf-8') as inFile:
                for line in inFile.readlines():
                    match = re.match(VERSION_REGEX, line)
                    if match:
                        return match.group(1)
        except:
            with open(file_name, 'r') as inFile:
                for line in inFile.readlines():
                    match = re.match(VERSION_REGEX, line)
                    if match:
                        return match.group(1)
    except IOError:
        pass

    # no joy, so try getting the version from a VERSION.txt file.
    try:
        file_name = os.path.join(os.getcwd(), 'fullmonty', 'VERSION.txt')
        with open(file_name, 'r') as inFile:
            return inFile.read().strip()
    except IOError:
        pass

    # no joy again, so return default
    return '0.0.0'

# all versions of python
required_imports = [
    'six',
]

# libraries that have been moved into python
print("Python (%s)" % sys.version)
if sys.version_info < (3, 1):
    required_imports.extend([
        'ordereddict',  # new in py31
        'decorator',
    ])

if sys.version_info < (3, 2):
    required_imports.extend([
        "argparse",  # new in py32
        "configparser",  # back port from py32
    ])

setup(
    name='FullMonty',
    version=get_project_version(),
    author='Roy Wright',
    author_email='roy@wright.org',
    url='http://fullmonty.example.com',
    packages=['fullmonty'],
    package_dir={'': '.'},
    package_data={'fullmonty': ['*.txt', '*.js', '*.html', '*.css'],
                  'tests': ['*'],
                  '': ['*.rst', '*.txt', '*.rc', '*.in']},
    license='license.txt',
    description='Eclectic library for applications.',
    long_description=open('README.rst').read(),
    # use keywords relevant to the application
    keywords=[],
    # use classifiers from:  https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    install_requires=required_imports,
    entry_points={
        'console_scripts': ['fullmonty = fullmonty.fullmonty_main:main']
    })
