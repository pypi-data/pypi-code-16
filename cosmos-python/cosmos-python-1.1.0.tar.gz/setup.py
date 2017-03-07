# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cosmos-python',

    version='1.1.0',

    description='The Python SDK for CosMoS, the universal cms.',
    long_description=long_description,

    url='https://github.com/cosmos-cms/cosmos-python',

    author='Marius Birkhoff',
    author_email='mariusbirkhoff@hotmail.com',

    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='cosmos universal cms',

    packages=["Cosmos", "Cosmos.Exceptions", "Cosmos.Security", "Cosmos.Storage"],

    package_dir = { "Cosmos": "src/Cosmos" },

    install_requires=['pycryptodomex'],

)
