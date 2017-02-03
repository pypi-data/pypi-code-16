from src.cleaner_ecr import EcrCleaner
import mock


class TestCleanEcrShould(object):
    @mock.patch('botocore.client.BaseClient._make_api_call')
    def test_delete_all_repositories_if_tag_is_none(self, mock_connection):
        tag = None
        ecr_clean = EcrCleaner(mock_connection, tag)
        assert ecr_clean.delete_all_repositories.called
