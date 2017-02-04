# -*- coding:utf-8 -*-
import os
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='yacbv',
    version='0.2.0',
    description='Yet another class based views for Django',
    long_description=readme,
    author="Daniel Czuba",
    author_email='dc@danielczuba.pl',
    url='https://github.com/Alkemic/yaCBV',
    license='MIT',
    packages=['yacbv'],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='django,cbv,class based views',
)
