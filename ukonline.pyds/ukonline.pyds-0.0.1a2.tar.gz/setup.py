# setup.py
# Author: Sébastien Combéfis
# Version: March 24, 2017

from setuptools import find_packages, setup

setup(
    name='ukonline.pyds',
    version='0.0.1a2',
    description='Data structures implementations in Python for pedagogical purpose.',
    url='https://github.com/ukonline/pyds',
    author='UKOnline',
    author_email='info@ukonline.be',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries'
    ],
    keywords='data-structures',
    packages=find_packages(exclude=['contrib', 'docs', 'tests'])
)