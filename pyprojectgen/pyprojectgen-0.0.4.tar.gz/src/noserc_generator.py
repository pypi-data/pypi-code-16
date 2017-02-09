""".noserc file generator module."""

NOSERC_TEMPLATE = \
"""
[nosetests]
verbosity=3
with-doctest=1
with-coverage=1
cover-package=src
"""

class NosercGenerator(object):
    """.noserc file generator class."""

    @staticmethod
    def generate(file_path):
        """Generate .noserc file for the project."""
        with open(file_path, 'w') as stream:
            stream.write(NOSERC_TEMPLATE)
