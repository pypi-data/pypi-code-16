import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(

    name='timeswitch',
    version='1.0.0',

    description='Test date/time against a time period expressed in a simple grammar',
    long_description=(read('README.md')),

    url='https://bitbucket.org/rocketboots/timeswitch/',
    author='RocketBoots Pty Ltd',
    author_email='support@rocketboots.com',

    packages=find_packages(exclude=['test*']),
    include_package_data=True,

    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='date time range period expression language',

    install_requires=[
        'pyparsing~=2.1',
        'enum34~=1.0'
    ],

    extras_require={
        'test': [
            'coverage~=4.0',
            'mock~=1.3',
            'nose~=1.3',
            'testfixtures~=4.3'
        ]
    },

    entry_points={
        'console_scripts': [
            'timeswitch=timeswitch.__main__:main',
        ]
    }

)
