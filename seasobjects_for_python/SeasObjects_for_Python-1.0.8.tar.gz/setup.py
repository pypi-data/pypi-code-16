from setuptools import setup

install_requires = [ 'rdflib', 'rdflib-jsonld', 'simplejson', 'pytz', 'python-dateutil', 'PyCrypto' ]

setup(name='SeasObjects_for_Python',
    version='1.0.8',
    author='Asema Electronics Ltd',
    author_email='python_dev@asema.com',
    platform='noarch',
    license='BSD',
    description='SEAS RDF model manipulation in Python',
    long_description="""A communication library that allows handling SEAS semantic messages as objects. Automatically handles object parsing and serialization to multiple transfer formats and offers various helper methods for the communication.""",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
    ],
    url='https://seas.asema.com',
    py_modules=['SeasObjects/__init__'],
    packages=['SeasObjects/agents', 'SeasObjects/common', 'SeasObjects/factory', 'SeasObjects/model', 'SeasObjects/rdf', 'SeasObjects/seasexceptions'],
    install_requires=install_requires
    )
