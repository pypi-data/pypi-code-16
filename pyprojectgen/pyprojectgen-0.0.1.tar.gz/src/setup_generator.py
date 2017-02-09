"""Setup file generator module."""

SETUP_TEMPLATE = """
\"\"\"Project setup script.\"\"\"
from setuptools import setup, find_packages
from os import path
import metadata

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
long_description = ""

# try:
#     from pypandoc import convert
#     if path.exists(path.join(here, 'README.md')):
#         long_description = convert('README.md', 'rst')
# except ImportError:
#     print("warning: pypandoc module not found, could not convert Markdown to RST")

setup(
    name=metadata.NAME,
    version=metadata.VERSION,
    description=metadata.DESCRIPTION,
    long_description=long_description,
    url=metadata.URL,
    author=metadata.AUTHOR,
    author_email=metadata.AUTHOR_EMAIL,
    license=metadata.LICENSE,
    classifiers=metadata.CLASSIFIERS,
    packages=find_packages(exclude=[]),
    setup_requires=metadata.SETUP_REQUIRES,
    test_suite=metadata.TEST_SUITE,
    tests_require=metadata.TESTS_REQUIRES,
    entry_points={
        'console_scripts': []
    },
)
"""

class SetupGenerator(object):
    """Setup file generator class."""

    @staticmethod
    def generate(file_path):
        """Generates the project setup.py file."""
        with open(file_path, 'w') as stream:
            stream.write(SETUP_TEMPLATE)
