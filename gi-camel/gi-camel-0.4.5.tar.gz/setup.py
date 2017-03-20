# coding: utf-8

import sys
from setuptools import setup

if sys.version_info < (3,3):
    print("At least Python 3.3 is required for camel.", file=sys.stderr)
    exit(1)
try:
    from setuptools import setup
except ImportError:
    print("Please install setuptools before installing camel.", file=sys.stderr)
    exit(1)

# set __version__ and DESCRIPTION
exec(open("camel/version.py").read())

setup(
    name='gi-camel',
    version=__version__,
    author='Christopher Schröder and Sven Rahmann',
    author_email='christopher.schroeder@tu-dortmund.de, sven.rahmann@uni-due.de',
    description=DESCRIPTION,
    zip_safe=False,
    license='MIT',
    url='https://bitbucket.org/christopherschroeder/camel',
    packages=['camel', 'camel.modules', 'camel.wrap', 'camel.helper'],
    entry_points={
        "console_scripts":
            ["camel = camel.camel:run",
            ]
        },
    package_data={'': ['*.css', '*.sh', '*.html']},
    install_requires=['numpy', 'scipy', 'seaborn', 'matplotlib'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)

