from setuptools import setup, find_packages
import py_hangman

LONG_DESCRIPTION = """
This is a simple text-based 2-player version of Hangman.
More description will be added later.

This project supports Python 2.7 and Python 3.2 and higher.
"""

PROJECT_CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Intended Audience :: End Users/Desktop',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Games/Entertainment',
    'Topic :: Games/Entertainment :: Puzzle Games',
]

setup(
    name="py_hangman",
    version=py_hangman.__version__,
    license="MIT",
    description="A 2-player version of Hangman",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/prasadkatti/py_hangman",
    author="Prasad Katti",
    author_email="prasadmkatti@gmail.com",
    packages=find_packages(),
    keywords='games hangman',
    classifiers=PROJECT_CLASSIFIERS,
    entry_points={
        'console_scripts': [
            'hangman=py_hangman.hangman:main',
        ],
    },
    install_requires=['six']
)
