"""Project Configuration module."""
import yaml

class ProjectConfiguration(object):
    """Project Configuration class."""
    def __init__(self, conf_path):
        with open(conf_path, 'r') as stream:
            data = yaml.load(stream)
            self.metadata = data['metadata']
            self.readme = data['readme']
            self.license = data['license']
