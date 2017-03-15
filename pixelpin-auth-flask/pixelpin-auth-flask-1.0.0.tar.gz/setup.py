# -*- coding: utf-8 -*-
"""Setup file for easy installation"""
from os.path import join, dirname
from setuptools import setup


def long_description():
    return open(join(dirname(__file__), 'README.md')).read()

def load_requirements():
    return open(join(dirname(__file__), 'requirements.txt')).readlines()

setup(
    name='pixelpin-auth-flask',
    version=__import__('pixelpin_auth_flask').__version__,
    author='Matias Aguirre, Callum Brankin',
    author_email='callum@pixelpin.co.uk',
    description='Python Social Authentication, Flask integration.',
    license='BSD',
    keywords='flask, social auth, pixelpin, pixelpin auth',
    url='https://github.com/PixelPinPlugins/pixelpin-auth-flask',
    packages=['pixelpin_auth_flask'],
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
