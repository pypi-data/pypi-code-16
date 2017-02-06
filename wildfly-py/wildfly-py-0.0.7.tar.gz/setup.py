#!/usr/bin/env python

# Setuptools install description file.

from setuptools import setup, find_packages

with open('README.md') as readme:
    long_description = readme.read()

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name='wildfly-py',
    version='0.0.7',
    description='WildFly Management Python API',
    long_description=long_description,
    zip_safe=True,
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
    entry_points={
        'console_scripts': ['wildfly-py = wildfly.__main__:main'],
        'setuptools.installation': ['eggsecutable = wildfly.__main__:main'],
    },
    author='CENX',
    author_email='devops@cenx.com',
    license='Apache License 2.0',
    keywords='cenx wildfly',
    url='https://github.org/cenx-cf/wildfly-py')
