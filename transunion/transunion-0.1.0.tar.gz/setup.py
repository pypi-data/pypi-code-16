from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='transunion',
    version='0.1.0',
    description='TransUnion Python API',
    long_description='Python module for TransUnion Credit Report API',
    url='',
    author='Hang Xu',
    author_email='hang@parasail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='transunion transunion-python api',
    packages=find_packages(exclude=['tests']),
    install_requires=['args', 'clint', 'configparser', 'cookies', 'defusedxml',
                      'dicttoxml', 'enum34', 'funcsigs', 'mccabe', 'mock',
                      'pbr', 'pkginfo', 'pycodestyle', 'requests',
                      'requests-toolbelt', 'responses', 'setuptools', 'six',
                      'twine', 'wheel', 'xmltodict', 'cached-property']
)
