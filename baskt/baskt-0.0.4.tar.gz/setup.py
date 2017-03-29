# from distutils.core import setup
from setuptools import setup, find_packages

__version__ = None
with open('baskt/version.py') as f:
    exec(f.read())

setup(name = "baskt",
    version=str(__version__),
    description="This library allows you to quickly and easily use the Baskt API via Python.",
    author="Baskt Development Team",
    author_email="hello@baskt.xyz",
    license="MIT",
    url="https://github.com/baskt/baskt-python",
    long_description='Please see our GitHub README',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers = [
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Database"
    ]
)
