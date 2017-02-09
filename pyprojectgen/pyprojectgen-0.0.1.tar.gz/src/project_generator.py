"""Project generator module."""
from src.project_config import ProjectConfiguration
from src.project_structure_generator import ProjectStructureGenerator
from src.metadata_generator import MetadataGenerator
from src.setup_generator import SetupGenerator
from src.tox_generator import ToxGenerator
from src.gitignore_generator import GitignoreGenerator
from src.readme_generator import ReadmeGenerator
from src.license_generator import LicenseGenerator
from src.noserc_generator import NosercGenerator


class ProjectGenerator(object):
    """Project generator class."""

    def __init__(self, configuration):
        if not isinstance(configuration, ProjectConfiguration):
            raise ValueError('configuration is not of type ProjectConfiguration')
        self.configuration = configuration
        self.root_path = ''
        self.project_root = "/" + self.configuration.metadata['NAME']
        self.paths = {
            'metadata': '/metadata.py',
            'setup': '/setup.py',
            'tox': '/.tox.ini',
            'gitignore': '/.gitignore',
            'readme': '/README.md',
            'license': '/LICENSE',
            'noserc': '/.noserc'
        }

    def __get_path(self, key):
        if key == 'root':
            return self.project_root
        if key in self.paths:
            return self.project_root + self.paths[key]

    def generate(self, root_path):
        """Generates the project folder structure and files."""
        self.project_root = root_path + "/" + self.configuration.metadata['NAME']
        ProjectStructureGenerator.generate(self.__get_path('root'))
        MetadataGenerator.generate(self.configuration.metadata, self.__get_path('metadata'))
        SetupGenerator.generate(self.__get_path('setup'))
        ToxGenerator.generate(self.__get_path('tox'))
        GitignoreGenerator.generate(self.__get_path('gitignore'))
        if self.configuration.readme:
            ReadmeGenerator.generate(self.__get_path('readme'), self.configuration.readme)
        if self.configuration.license:
            LicenseGenerator.generate(self.__get_path('license'), self.configuration.license)
        NosercGenerator.generate(self.__get_path('noserc'))
        self.root_path = ''
