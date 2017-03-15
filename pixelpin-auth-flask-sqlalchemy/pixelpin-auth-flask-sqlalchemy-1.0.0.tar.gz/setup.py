# -*- coding: utf-8 -*-
"""Setup file for easy installation"""
from os.path import join, dirname
from setuptools import setup


def long_description():
    return open(join(dirname(__file__), 'README.md')).read()

def load_requirements():
    return open(join(dirname(__file__), 'requirements.txt')).readlines()

setup(
    name='pixelpin-auth-flask-sqlalchemy',
    version=__import__('pixelpin_auth_flask_sqlalchemy').__version__,
    author='Matias Aguirre, Callum Brankin',
    author_email='callum@pixelpin.co.uk',
    description='Python Social Authentication, SQLAlchemy Flask '
                'models integration.',
    license='BSD',
    keywords='flask, sqlalchemy, social auth, pixelpin, pixelpin auth',
    url='https://github.com/PixelPinPlugins/pixelpin-auth-flask-sqlalchemy',
    packages=['pixelpin_auth_flask_sqlalchemy'],
    long_description=long_description(),
    install_requires=load_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
    zip_safe=False
)
