import os
import codecs
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()


setup(
    name='faas',
    version="0.0.1",
    url='',
    author='Omer Duskin',
    author_email='dusking@gmail.com',
    license='LICENSE',
    platforms='All',
    description='',
    long_description=read('README.rst'),
    packages=['faas'],
    install_requires=[
    ],
    classifiers=[
        'Programming Language :: Python',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
