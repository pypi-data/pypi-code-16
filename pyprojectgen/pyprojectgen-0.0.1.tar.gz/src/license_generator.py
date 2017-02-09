"""License file generator module."""
from pathlib import Path
from src.license_templates import MIT_LICENSE_TEMPLATE
from src.license_templates import GPL3_LICENSE_TEMPLATE
from src.license_templates import APACHE_LICENSE_TEMPLATE

class LicenseGenerator(object):
    """License file generator class."""

    @staticmethod
    def generate(file_path, license_metadata):
        """Generates the LICENSE file for the project."""
        content = None
        if license_metadata['file'] == 'MIT':
            content = MIT_LICENSE_TEMPLATE
            if 'year' in license_metadata:
                content = content.replace('<year>', license_metadata['year'])
            if 'owner' in license_metadata:
                content = content.replace('<owner>', license_metadata['owner'])
        elif license_metadata['file'] == 'GPL3':
            content = GPL3_LICENSE_TEMPLATE
        elif license_metadata['file'] == 'Apache':
            content = APACHE_LICENSE_TEMPLATE

        if content:
            with open(file_path, 'w') as stream:
                stream.write(content)
        else:
            Path(file_path).touch()
