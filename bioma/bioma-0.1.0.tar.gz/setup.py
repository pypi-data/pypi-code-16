"""Setup script."""


from setuptools import setup, find_packages

setup(
    name='bioma',
    version='0.1.0',
    description='Bio-related data management using graph databases and web '
                'semantics.',
    long_description='''bioma is a bio-related data manager, designed to ease
                        the storage, manipulation and exchange of information
                        in scientific research. The system is built on top of
                        graph databases and web semantics techniques, that
                        differently from conventional relational databases
                        allows adaptive growth of datasets, unconstrained by a
                        previously defined data structure. Querying algorithms
                        and a simplistic data representation (easily exported)
                        are also included in the package.''',
    url='https://github.com/dmrib/bioma',
    author='Danilo Miranda Ribeiro',
    author_email='dmrib.cs@gmail.com',
    license='MIT',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.6',
                 'Intended Audience :: Science/Research'],
    keywords='bio web semantics graph database',
    packages=find_packages(),
    install_requires=['pytest', 'jsonpickle'],
)
