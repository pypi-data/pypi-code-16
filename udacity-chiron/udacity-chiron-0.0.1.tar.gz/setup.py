from setuptools import setup

setup(
    name='udacity-chiron',
    version='0.0.1',
    author='S. Charles Brubaker',
    author_email='cb@udacity.com',
    packages=['udacity_chiron'],
    entry_points={
        'console_scripts': [
            'udacity = udacity_chiron.chiron:main_func',
            'chiron = udacity_chiron.chiron:main_func'
        ],
    },
    include_package_data=True,
    url='http://github.com/udacity/udacity-chiron',
    license='MIT',
    description='CLI tool for interacting with Chiron feedback service.',
    keywords = 'Udacity',
    long_description=open('README.rst').read(),
    install_requires=[
        "requests >= 2.2.1",
        "requests-toolbelt >= 0.7.0",
        "future"
    ],
)