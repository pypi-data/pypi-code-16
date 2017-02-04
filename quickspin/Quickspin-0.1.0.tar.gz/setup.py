from distutils.core import setup

setup(
    # Application name:
    name="Quickspin",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="V3ckt0r",
    author_email="",

    # Packages
    packages=["Quickspin"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/Quickspin/",

    #
    license="LICENSE.txt",
    description="Quickspin CLI tool for managing AWS resources",

    long_description=open("README.md").read(),

    # Dependent packages (distributions)
    install_requires=[
        "boto3",
    ],
)
