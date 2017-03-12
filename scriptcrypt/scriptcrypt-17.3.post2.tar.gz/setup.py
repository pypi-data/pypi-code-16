from setuptools import setup, find_packages
from codecs import open
from os import path
import scriptcrypt.version
import sys


here = path.abspath(path.dirname(__file__))

if not sys.version_info[0] == 3 and \
       sys.version_info[1] >= 5:
    sys.exit("Sorry, Python 3.5 or higher only")

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scriptcrypt',
    version=scriptcrypt.version.version,
    description='Custom script notebook',
    long_description=long_description,
    url='https://bitbucket.com/seregaxvm/scriptcrypt',
    author='S.V. Matsievskiy',
    author_email='matsievskiysv@gmail.com',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: GNU General Public \
License v3 or later (GPLv3+)',
        'Environment :: Console :: Curses',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='script database',
    packages=find_packages(exclude=["*.tests",
                                    "*.tests.*",
                                    "tests.*",
                                    "tests"]),
    include_package_data=True,
    install_requires=['sqlalchemy', 'docopt'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['nose'],
    },
    entry_points={
        'console_scripts': ['scriptcrypt = scriptcrypt.__main__:main']
    }
)
