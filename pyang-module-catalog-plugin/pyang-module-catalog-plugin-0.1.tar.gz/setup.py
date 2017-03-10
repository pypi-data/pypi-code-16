import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pyang-module-catalog-plugin',
    version='0.1',
    description=('A pyang plugin to extract OpenConfig module catalog data from YANG modules'),
    long_description=read('README.md'),
    packages=['modulecatalog'],
    author='Carl Moberg',
    author_email='camoberg@cisco.com',
    license='New-style BSD',
    url='https://github.com/cmoberg/pyang-module-catalog-plugin',
    install_requires=['pyang'],
    include_package_data=True,
    keywords=['yang', 'extraction'],
    classifiers=[],
    entry_points={'pyang.plugin': 'module_catalog_plugin=modulecatalog:pyang_plugin_init'}
)
