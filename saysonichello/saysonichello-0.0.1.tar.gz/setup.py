# -*- coding:utf8 -*-
from setuptools import setup, find_packages

setup(
    name='saysonichello',
    version='0.0.1',

    description='A Sample SayHello Python project',
    long_description='''SayHello DESC''',

    # The project's main homepage.
    url='https://github.com/ultrakain/sayhello',

    # Author details
    author='Sonic',
    author_email='ultrakain@gmail.com',

    # Choose your license
    license='MIT',

    # What does your project relate to?
    keywords='sample setuptools development',

    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['requests'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'saysonichello=say_hello:main',
        ],
    },
)