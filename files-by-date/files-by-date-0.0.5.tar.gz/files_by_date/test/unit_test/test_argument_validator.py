from unittest.mock import patch

import pytest

from files_by_date.validators.argument_validator import ArgumentValidator


@patch('files_by_date.validators.argument_validator.os')
def test_validate_input_dir(os):
    os.path.exists = lambda x: True
    os.access = lambda x, y: True
    ArgumentValidator.validate_input_dir('test')

    os.path.exists = lambda x: False
    with pytest.raises(AssertionError):
        ArgumentValidator.validate_input_dir('test')

    os.path.exists = lambda x: True
    os.access = lambda x, y: False
    with pytest.raises(AssertionError):
        ArgumentValidator.validate_input_dir('test')


@patch('files_by_date.validators.argument_validator.os')
def test_validate_target_dir(os):
    os.path.exists = lambda x: False
    os.access = lambda x, y: True
    ArgumentValidator.validate_target_dir('test')

    os.access = lambda x, y: False
    with pytest.raises(AssertionError):
        ArgumentValidator.validate_target_dir('test')
