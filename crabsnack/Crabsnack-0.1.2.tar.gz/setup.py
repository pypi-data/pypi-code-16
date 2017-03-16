import os
from setuptools import setup
import functools

_in_dir = functools.partial(os.path.join, os.path.dirname(__file__))

with open(_in_dir("crabsnack", "__version__.py")) as vf:
    exec(vf.read())
# ___________________________________


def readme():
    with open('README.rst', 'rb') as f:
        return f.read()
# ___________________________________


setup(
    name='Crabsnack',
    version=__version__, # noqa
    description='The best sea food in the world',
    long_description=readme(),

    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],

    include_package_data=True,
    url='http://github.com/victorziv/crabsnack',
    author='Eugene H. Krabs',
    author_email='mrkrabs@bottom.com',
    license='MIT',
    packages=['crabsnack'],
    zip_safe=False,
    install_requires=[
        'markdown',
    ]
)
