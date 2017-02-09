"""Project structure generator module."""
from pathlib import Path
from src.file_folder_creators import create_folder

class ProjectStructureGenerator(object):
    """Project structure generator class."""

    @staticmethod
    def generate(project_path):
        """Generates the project folder structure."""
        src_path = project_path + '/src'
        tests_path = project_path + '/tests'
        create_folder(project_path)
        create_folder(src_path)
        Path(src_path + '/__init__.py').touch()
        create_folder(tests_path)
        Path(tests_path + '/__init__.py').touch()
