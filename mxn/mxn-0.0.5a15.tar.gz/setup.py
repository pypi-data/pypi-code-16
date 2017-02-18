import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="mxn",
    version="0.0.5a15",
    author="Rostislav Chudoba, Vladimir Vancik",
    author_email="rostislav.chudoba@rwth-aachen.de",
    description=("Tool for determination of interaction envelope "
                 "of a composite cross-section."),
    license="BSD",
    keywords="moment-normal force interaction",
    url="http://packages.python.org/mxn",
    install_requires=['traits>=4.0.0',
                      'traitsui>=4.0.0',
                      'pyface>=4.0.0',
                      'numpy>=1.10.0',
                      'scipy>=0.18.1',
                      'sympy>=1.0',
                      'matplotlib>=1.5.3'],
    packages=find_packages(),
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.md', '*.rst'],
    },
    long_description='',
    entry_points={
        'gui_scripts': [
            'mxn = mxn.scripts.mxnapp:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
