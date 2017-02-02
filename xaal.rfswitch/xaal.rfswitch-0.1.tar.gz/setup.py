from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

VERSION = "0.1"

setup(
    name='xaal.rfswitch',
    version=VERSION,
    license='GPL License',
    author='Jerome Kerdreux',
    author_email='Jerome.Kerdreux@imt-atlantique.fr',
    #url='',
    description=('A xAAL gateway for bugOne network'),
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['xaal', 'HQProduct', 'rf','wireless'],
    platforms='any',
    packages=["xaal.rfswitch"],
    namespace_packages=["xaal"],
    include_package_data=True,
    install_requires=[
        'xaal-lib'
    ]
)
