# -*- coding: utf-8 -*-
import setuptools


setuptools.setup(name='specpie',
                 version='1.1.3-1',
                 description='A BDD-like test framework',
                 author='mralves',
                 author_email='mateusra@id.uff.br',
                 url='https://github.com/mralves/specpie',
                 py_modules=['specpie'],
                 packages=setuptools.find_packages(exclude=['examples', 'tests']),
                 install_requires=['colorama', 'coverage'],
                 license='MIT License',
                 scripts=['bin/specpie'],
                 zip_safe=False,
                 keywords='test bdd',
                 classifiers=[])
