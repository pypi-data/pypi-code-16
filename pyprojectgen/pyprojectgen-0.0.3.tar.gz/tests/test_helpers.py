import os
import yaml

test_configuration = {
    'license': {
        'file': 'MIT',
        'name': 'MIT'
    },
    'metadata': {
        'AUTHOR': 'Tester',
        'AUTHOR_EMAIL': 'test@test.com',
        'CLASSIFIERS': [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.5'
        ],
        'DESCRIPTION': 'Generates python project structure',
        'EXCLUDE': [
            'tests'
        ],
        'KEYWORDS': '',
        'LICENSE': 'MIT',
        'NAME': 'pyprojectgen',
        'SETUP_REQUIRES': [
            'nose>=1.0',
            'coverage>=4.0.3'
        ],
        'TESTS_REQUIRES': [
            'nose'
        ],
        'TEST_SUITE': 'nose.collector',
        'URL': 'https://github.com/Tester/test',
        'VERSION': '0.0.1'
    },
    'readme': {
        'description': 'Generate base file structure for python project required for creating a python package.',
        'header': 'Python project generator'
    }
}

def create_project_conf_file(conf_path, file_path, configuration):
    """Create conf file and folder."""
    if not os.path.exists(conf_path):
        os.mkdir(conf_path)
    with open(file_path, 'w') as stream:
        content = yaml.dump(configuration, default_flow_style=False)
        stream.write(content)

def remove_project_conf_file(conf_path, file_path):
    """Remove conf file and folder."""
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(conf_path):
        os.rmdir(conf_path)
