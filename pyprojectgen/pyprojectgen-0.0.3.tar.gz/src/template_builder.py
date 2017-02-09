"""Template builder module."""
import json
import yaml


class TemplateBuilder(object):
    """Template builder class."""
    @staticmethod
    def create_template_data():
        """Creates a dictionary containing project metadata keys."""
        template_data = {
            'metadata': {
                'NAME': '',
                'VERSION': '',
                'DESCRIPTION': '',
                'URL': '',
                'AUTHOR': '',
                'AUTHOR_EMAIL': '',
                'LICENSE': '',
                'KEYWORDS': '',
                'CLASSIFIERS': [
                    'Development Status :: 3 - Alpha',
                    'Intended Audience :: Developers',
                    'Topic :: Software Development :: Libraries',
                    'License :: OSI Approved :: MIT License',
                    'Programming Language :: Python :: 3.5',
                ],
                'EXCLUDE': [
                    'tests'
                ],
                'SETUP_REQUIRES': [
                    'nose>=1.0',
                    'coverage>=4.0.3',
                ],
                'TEST_SUITE': 'nose.collector',
                'TESTS_REQUIRES': ['nose']
            },
            'license': {
                'file': '',
                'file_comment': 'File options: MIT, GPL3, Apache, EMPTY',
                'owner' : '',
                'year' : ''
            },
            'readme': {
                'header': '',
                'description': ''
            }
        }
        return template_data

    @staticmethod
    def build_json():
        """Creates the json version of project metadata template."""
        result = TemplateBuilder.create_template_data()
        return json.dumps(result, indent=4, separators=(',', ': '))

    @staticmethod
    def build_yaml():
        """Creates the yaml version of project metadata template."""
        result = TemplateBuilder.create_template_data()
        return yaml.dump(result, default_flow_style=False)
