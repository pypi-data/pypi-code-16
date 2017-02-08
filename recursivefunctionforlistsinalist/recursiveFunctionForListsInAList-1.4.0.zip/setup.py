# This file contains metadata about your distribution

# Import the "setup" function from Python's distribution utilities
from distutils.core import setup
setup(
    # This will contain the setup function's argument names
    name = 'recursiveFunctionForListsInAList',
    version = '1.4.0',
    py_modules = ['recursiveFunctionForListsInAList'], # Associate your module's metadata with the setup function's argument
    author = 'Immanuel Kolapo',
    author_email = 'icaspian@outlook.com',
    url = 'http://www.caspianic.com',
    description= 'A simple printer of nested lists',
)