## Copyright (c) 2016-2017, Blake C. Rawlings.

import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme_text = f.read()

setuptools.setup(
    name='st2smv',
    version='0.1.2',
    author='Blake C. Rawlings',
    author_email='blakecraw@gmail.com',
    description=(
        'A tool to convert Structured Text PLC code to an SMV model.'
    ),
    license='GPLv3+',
    url='https://pypi.python.org/pypi/st2smv',
    packages=[
        'st2smv',
        'st2smv.plugins',
        'st2smv.plugins.connectivity',
        'st2smv.plugins.irrelevant_logic',
        'st2smv.plugins.stdlib',
        'st2smv.plugins.varlock',
    ],
    entry_points={
        'console_scripts': ['st2smv=st2smv.__main__:main']
    },
    long_description=readme_text,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
    ],
    install_requires=['networkx', 'pyparsing', 'six'],
    package_data={
        'st2smv': ['Makefile.run', '*.smv'],
    },
)
