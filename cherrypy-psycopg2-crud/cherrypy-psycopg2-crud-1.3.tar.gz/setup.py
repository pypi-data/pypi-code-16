from setuptools import setup
setup(
    name='cherrypy-psycopg2-crud',
    version='1.3',

    description="CherryPy page handler base-class to export psycopg2 database tables in a RESTful way",
    url="https://bitbucket.org/gclinch/cherrypy-psycopg2-crud",
    license='Apache License, Version 2.0',

    author='Graham Clinch',
    author_email='g.clinch@lancaster.ac.uk',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: CherryPy',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Database'],

    packages=['cherrypy_psycopg2_crud'],
    install_requires=['CherryPy', 'psycopg2', 'cherrypy-psycopg2'],
)
