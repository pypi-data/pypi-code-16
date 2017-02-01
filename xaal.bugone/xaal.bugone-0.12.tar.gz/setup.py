from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

VERSION = "0.12"

setup(
    name='xaal.bugone',
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
    keywords=['xaal', 'bugone', 'rfm12','wireless'],
    zip_safe=False,
    platforms='any',
    packages=["xaal.bugone","test"],
    include_package_data=True,
    install_requires=[
        'xaal-lib'
    ]
)
