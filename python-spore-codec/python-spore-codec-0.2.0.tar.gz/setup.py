# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='python-spore-codec',
    version='0.2.0',
    description='Spore codec for CoreAPI specification',
    long_description=readme,
    author='Arnaud Grausem',
    author_email='arnaud.grausem@gmail.com',
    url='https://github.com/unistra/python-spore-codec',
    license='GPLv3',
    include_package_data=True,
    install_requires=['coreapi'],
    # extra_requires={
    #     'test': ['coverage', 'pytest', 'pytest-cov']
    # },
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='coreapi spore api-description rest-api'
)
