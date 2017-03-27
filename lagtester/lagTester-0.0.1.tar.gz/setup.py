# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

long_description = "See website for more info."

setup(
    name='lagTester',

    version='0.0.1',

    description='Script to test gamepad lag time',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/owlz/lagTester',

    # Author details
    author='Michael Bann',
    author_email='self@bannsecurity.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],

    # What does your project relate to?
    keywords='gamepad controller lag test',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['inputs'],

    entry_points={
        'console_scripts': [
            'lagTester = lagTester.lagTester:main',
        ],
    },

)

