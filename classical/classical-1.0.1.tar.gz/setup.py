from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='classical',

    version='1.0.1',

    description='Class Tools for Python',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/altvod/classical',

    # Author details
    author='Grigory Statsenko',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='class utilities',

    packages=find_packages(exclude=['tests']),

    extras_require=dict(
        develop=[
            'pytest',
            'pytest-cov',
            'sphinx',
            'sphinx_rtd_theme',
        ]
    )
)