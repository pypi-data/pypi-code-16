import unittest

from jsonschema import ValidationError
from mock import patch
from the_ark.resources.schema_validator import validate, SchemaValidationError
from the_ark.resources.action_schema import ACTION_SCHEMA


class SchemaTestCase(unittest.TestCase):

    @patch('jsonschema.validate')
    def test_schema_validation_success(self, mock_validate):
        self.assertTrue(validate("data", "schema"))

    def test_action_list_schema(self):
        data = [
            {
                "action": "click",
                "css_selector": ".click"
            }
        ]

        self.assertTrue(validate(data, ACTION_SCHEMA))

    @patch('jsonschema.validate')
    def test_schema_validation_failure(self, mock_validate):
        mock_validate.side_effect = ValidationError("invalid!")
        with self.assertRaises(SchemaValidationError) as validation_error:
            validate("actions", ACTION_SCHEMA)

        self.assertIn("not valid", str(validation_error.exception))

    @patch('jsonschema.validate')
    def test_schema_unexpected_failure(self, mock_validate):
        mock_validate.side_effect = Exception("Boom!")
        with self.assertRaises(SchemaValidationError) as validation_error:
            validate("actions", ACTION_SCHEMA)

        self.assertIn("Unexpected", str(validation_error.exception))

    def test_schema_exception_to_dict(self):
        sve = SchemaValidationError("message")
        self.assertIn("message", sve.to_dict().keys())
        self.assertIn("code", sve.to_dict().keys())
        self.assertIn("details", sve.to_dict().keys())
