from setuptools import find_packages, setup

setup(
    name='hierarchical',
    version='0.0.6',
    description='Hierarchical interface to Python dictionaries',
    long_description='This package provides a file-system like interface for Python dictionaries, providing file/directory key access.',
    author='Eric Wong',
    author_email='ericwong@cs.cmu.edu',
    platforms=['any'],
    license="Apache 2.0",
    url='https://github.com/locuslab/hierarchical',
    packages=find_packages(),
    install_requires=[
    ]
)
