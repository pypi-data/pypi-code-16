#!/usr/bin/env python
from setuptools import find_packages, setup

project = "ontology-alchemy"
version = "0.2.0"

setup(
    name=project,
    version=version,
    description="RDF Ontologies made easy",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/ontology-alchemy",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="ontology-alchemy",
    install_requires=[
        "contextlib2>=0.5.4",
        "rdflib>=4.2.1",
        "six>=1.10.0",
        "toposort>=1.4",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    tests_require=[
        "coverage>=3.7.1",
        "mock>=1.0.1",
        "nose-parameterized>=0.5.0",
        "PyHamcrest>=1.8.5",
    ],
)
