# -*- coding:utf-8 -*-
import os
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='yaacl',
    version='0.8.2',
    description='Yet another access control list (ACL) per view for Django',
    long_description=readme,
    author="Daniel Czuba",
    author_email='dc@danielczuba.pl',
    url='https://github.com/Alkemic/yaACL',
    license='MIT',
    packages=['yaacl'],
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
    keywords='django,acl,admin',
)
