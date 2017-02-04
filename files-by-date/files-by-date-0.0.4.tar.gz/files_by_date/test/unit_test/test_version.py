from unittest import mock
from unittest.mock import patch

from files_by_date.utils.version import get_version, update_version


@patch('files_by_date.utils.version.os')
def test_validate_input_dir(os):
    with mock.patch('builtins.open', mock.mock_open(read_data='0.0.1')):
        assert '0.0.1' == get_version()


@patch('files_by_date.utils.version.os')
def test_update_version(os):
    with mock.patch('builtins.open', mock.mock_open(read_data='0.0.1')):
        assert not update_version()
