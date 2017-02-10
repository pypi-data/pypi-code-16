from setuptools import setup, find_packages

import sebureem

setup(
    name='sebureem',
    version=sebureem.__version__,
    description="A simple comment server",
    long_description=open('README.rst').read(),
    url='https://framagit.org/Erwhann-Rouge/sebureem',
    author='Guilhem "Erwhann-Rouge" MAS-PAITRAULT',
    author_email="guilhem.mas-paitrault@protonmail.com",
    license='BSD-3-Clause/CECILL-B',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    keywords='sebureem comments disqus',
    packages=find_packages(),
    install_requires=[
        'flask>=0.12',
        'docopt>=0.6',
        'peewee>=2.8',
    ],
    entry_points={
        'console_scripts': [
            'sebureem=sebureem.cli:sebureem',
        ],
    },
)

