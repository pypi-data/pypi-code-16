import datetime
import os
import shutil
from unittest import TestCase
from unittest.mock import patch

import pytest

from files_by_date.validators.argument_validator import ArgumentValidator


class TestIntegrationArgumentValidator(TestCase):
    # TEST_DIR = f'./{datetime.datetime.now().microsecond}' # 3.6
    TEST_DIR = './{time}'.format(time=datetime.datetime.now().microsecond)

    def setUp(self):
        os.makedirs(TestIntegrationArgumentValidator.TEST_DIR)

    def tearDown(self):
        if os.path.exists(TestIntegrationArgumentValidator.TEST_DIR):
            shutil.rmtree(TestIntegrationArgumentValidator.TEST_DIR)

    def test_validate_input_dir(self):
        assert not ArgumentValidator.validate_input_dir(TestIntegrationArgumentValidator.TEST_DIR)
        with pytest.raises(AssertionError):
            # ArgumentValidator.validate_input_dir(f'{TestIntegrationArgumentValidator.TEST_DIR}_x')
            ArgumentValidator.validate_input_dir(
                '{test_dir}_x'.format(test_dir=TestIntegrationArgumentValidator.TEST_DIR))

    def test_validate_target_dir(self):
        # assert not ArgumentValidator.validate_target_dir(f'{TestIntegrationArgumentValidator.TEST_DIR}')
        # assert not ArgumentValidator.validate_target_dir(f'{TestIntegrationArgumentValidator.TEST_DIR}_x')
        assert not ArgumentValidator.validate_target_dir(
            '{test_dir}'.format(test_dir=TestIntegrationArgumentValidator.TEST_DIR))
        assert not ArgumentValidator.validate_target_dir(
            '{test_dir}_x'.format(test_dir=TestIntegrationArgumentValidator.TEST_DIR))

    @patch('files_by_date.validators.argument_validator.os')
    def test_validate_target_dir_with_exception(self, os):
        os.access = lambda x, y: False

        with pytest.raises(AssertionError):
            ArgumentValidator.validate_target_dir('test')
