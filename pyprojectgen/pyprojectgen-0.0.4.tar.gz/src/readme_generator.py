"""README.md file generator module."""

README_TEMPLATE = \
"""
# <header>

<description>
"""

class ReadmeGenerator(object):
    """README.md file generator class."""

    @staticmethod
    def generate(file_path, readme_metadata):
        """Generates the REAMDE.md file for the project."""
        content = README_TEMPLATE.replace("<header>", readme_metadata['header']) \
                .replace("<description>", readme_metadata['description'])
        with open(file_path, 'w') as stream:
            stream.write(content)
