from codecs import open
from os import path
from setuptools import setup

setup(
    name = 'axsemantics-cli',
    version = '0.1.3-1',

    description = 'AXSemantics API client Commandline Interface',

    # url = 'https://github.com/axsemantics/axsemantics-cli',

    author = 'Ramon Klass',
    author_email = 'ramon.klass@ax-semantics.com',

    license = 'MIT',

    classifiers = [
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages = ['axsemantics_cli', 'axsemantics_cli.common'],
    package_data = {'axsemantics_cli': ['importer.out']},
    include_package_data = True,

    install_requires = [
        'axsemantics',
        'click',
        'colorama',
    ],
    entry_points='''
        [console_scripts]
        axsemantics=axsemantics_cli.main:cli
        axsemantics-atml=axsemantics_cli.analyze:atml3file
        axsemantics-convert-bmecat=axsemantics_cli.convert_bmecat:convert_bmecat
    ''',
)
