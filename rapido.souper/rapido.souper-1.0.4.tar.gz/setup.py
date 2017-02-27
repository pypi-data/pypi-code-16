from setuptools import setup, find_packages
import os

version = '1.0.4'

setup(name='rapido.souper',
    version=version,
    description="Souper persistence for Rapido",
    long_description=open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='souper zodb rapido',
    author='Eric BREHAULT',
    author_email='ebrehault@gmail.com',
    url='https://github.com/collective/rapido.souper',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['rapido'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'souper',
        'rapido.core',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
