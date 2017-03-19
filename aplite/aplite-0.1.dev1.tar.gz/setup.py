from setuptools import setup

setup(
    name='aplite',
    version='0.1.dev1',
    url='https://github.com/barell/aplite',
    packages=['aplite',],
    license='MIT',
    long_description=open('README.rst').read(),
    entry_points={
        'console_scripts': [
            'aplite=aplite.cli:main'
        ]
    },
)