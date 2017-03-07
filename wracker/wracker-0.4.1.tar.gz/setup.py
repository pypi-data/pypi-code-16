"""Wracker package definition."""
from setuptools import setup
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import wracker


with open('README.md') as readme_file:
    readme = readme_file.read()


setup(
    name="wracker",
    version=wracker.__version__,
    description="A Bundler clone for Python",
    long_description=readme,
    url='https://github.com/dan-passaro/wracker',
    author='Dan Passaro',
    author_email='danpassaro@gmail.com',
    license=('License :: OSI Approved :: GNU Affero General Public License v3 '
             'or later (AGPLv3+)'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
    platforms=[
        'Operating System :: POSIX',
    ],

    package_dir={'': 'src'},
    packages=[
        'wracker',
        'wracker.pkg_resources',
    ],
    entry_points={
        'console_scripts': [
            'wracker=wracker.__main__:main',
        ],
    },
)
