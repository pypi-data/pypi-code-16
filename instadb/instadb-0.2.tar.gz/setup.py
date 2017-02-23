
from distutils.core import setup
from setuptools import find_packages

required = [
    "pandas>=0.15.2",
    "psycopg2==2.6.2"
]

setup(
    name="instadb",
    version="0.2",
    author="Mathieu Ripert",
    author_email="mathieu@instacart.com",
    url="https://github.com/mathieuripert/instadb",
    license="BSD",
    packages=find_packages(),
    package_dir={"instadb": "instadb"},
    description="A simple and light DB package",
    install_requires=required,
    classifiers=[
        # Maturity
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # License
        'License :: OSI Approved :: BSD License',
        # Versions supported
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

)
