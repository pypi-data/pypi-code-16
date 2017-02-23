# -*- coding: utf-8 -*-

from os.path import dirname, join
from setuptools import setup, find_packages


with open(join(dirname(__file__), 'ant2mvn/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()


setup(
    name='ant2mvn',
    version=version,
    url='http://techoffee.me',
    description='Making move Ant to Maven be easier',
    long_description=open('README.md').read(),
    author='Mario',
    maintainer='Mario',
    maintainer_email='hengliang.jia@gmail.com',
    license='MIT',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['ant2mvn = ant2mvn.command_line:main']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'docopt==0.6.2',
        'requests==2.11.1',
        'Jinja2==2.8'
    ],
)