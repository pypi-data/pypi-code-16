from unittest import TestCase
from src.template_builder import TemplateBuilder
import json
import yaml


class TestTemplateBuilder(TestCase):

    def setUp(self):
        self.expected_dict = {
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

    def test_create_setup_data(self):
        result = TemplateBuilder.create_template_data()
        self.assertEqual(self.expected_dict, result)

    def test_create_setup_json(self):
        result = TemplateBuilder.build_json()
        expected = json.dumps(self.expected_dict, indent=4, separators=(',', ': '))
        self.assertEqual(expected, result)

    def test_create_setup_yaml(self):
        result = TemplateBuilder.build_yaml()
        expected = yaml.dump(self.expected_dict, default_flow_style=False)
        self.assertEqual(expected, result)
