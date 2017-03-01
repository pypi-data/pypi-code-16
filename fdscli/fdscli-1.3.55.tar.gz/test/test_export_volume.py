#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.common.repository import Repository
from fdscli.model.volume.safeguard_preset import SafeGuardPreset
from fdscli.model.volume.volume import Volume
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.volume_service import VolumeService
from fdscli.utils.converters.common.repository_converter import RepositoryConverter
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

def mock_post( session, url, data ):
    print url

def mock_get_url_preamble():
    return "http://localhost:7777/fds/config/v09"

class VolumeExportTest( BaseCliTest ):
    '''
    Test case for volume export. IS-A unittest.TestCase.
    '''
    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch("fdscli.services.volume_service.VolumeService.export_volume", side_effect=mock_functions.exportVolume)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_export_volume(self, mockGetVolume, mockExportVolume, mockListTasks, mockTabular, mockPretty):
        '''
        The volume service calls are replaced by mock functions.

        Parameters
        ----------
        mockGetVolume (unittest.mock.MagicMock)
        mockExportVolume (unittest.mock.MagicMock)
        mockListTasks (unittest.mock.MagicMock)
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''
        args = ["volume", "export", "-volume_id=3", "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockExportVolume.call_count == 1

        volume = mockExportVolume.call_args[0][0]

        assert volume.id == 3

        repo = mockExportVolume.call_args[0][1]

        j_repo = RepositoryConverter.to_json(repo)
        print j_repo

        assert repo.url == "https://s3.amazon.com"
        assert repo.bucket_name == "xvolrepo"
        assert repo.remote_om == None
        assert repo.credentials.access_key_id == "ABCDEFG"
        assert repo.credentials.secret_key == "/52/yrwhere"

        print("test_export_volume passed.\n\n")

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch("fdscli.services.volume_service.VolumeService.export_volume", side_effect=mock_functions.exportVolume)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_export_volume_error(self, mockServiceGetVolume, mockServiceExportVolume, mockListTasks, mockTabular, mockPretty):
        '''
        Should not call VolumeService.export_volume when volume does not exist.

        Parameters
        ----------
        mockGetVolume (unittest.mock.MagicMock)
        mockExportVolume (unittest.mock.MagicMock)
        mockListTasks (unittest.mock.MagicMock)
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''
        args = ["volume", "export", "-volume_id=1", "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com"]

        self.callMessageFormatter(args)
        print("TRACE: Volume does not exist.")

        exception = None
        try:
            self.cli.run(args)
        except SystemExit as se:
            exception = se

        assert exception is None, "Unexpected exception"
        assert mockServiceExportVolume.call_count == 0

        args = ["volume", "export", "-volume_id=1", "--credential=missing_credential"]

        self.callMessageFormatter(args)
        print("TRACE: Volume does not exist.")

        try:
            self.cli.run(args)
        except SystemExit as se:
            exception = se

        assert exception is None, "Unexpected exception"
        assert mockServiceExportVolume.call_count == 0

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch("fdscli.services.volume_service.VolumeService.export_volume", side_effect=mock_functions.exportVolume)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_plugin_snapshot_id(self, mockServiceGetVolume, mockServiceExportVolume, mockListTasks, mockTabular, mockPretty):
        '''
        Command \'volume export -snapshot_id\' migrates an existing snapshot.
        Indirectly tests VolumePlugin.export_volume() by observing call to volume service.

        Parameters
        ----------
        mockServiceGetVolume (unittest.mock.MagicMock)
        mockServiceExportVolume (unittest.mock.MagicMock)
        mockListTasks (unittest.mock.MagicMock)
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''

        # Using mock in python, top level packages (like argparse) cannot be patched outright.
        # http://stackoverflow.com/questions/22750555/python-mock-patch-top-level-packages
        # TODO: Test parse_args() directly.

        print("Plugin test: volume export -snapshot_id")

        # Crucially, there is no -incremental specified.
        # Expected default value for that is False.
        args = ["volume", "export", "-volume_id=3", "-snapshot_id=7", "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockServiceExportVolume.call_count == 1

        from_last_export = mockServiceExportVolume.call_args[0][5]
        assert from_last_export == False

        snapshot_id = mockServiceExportVolume.call_args[0][2]
        assert snapshot_id == 7

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch("fdscli.services.volume_service.VolumeService.export_volume", side_effect=mock_functions.exportVolume)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_plugin_incremental(self, mockServiceGetVolume, mockServiceExportVolume, mockListTasks, mockTabular, mockPretty):
        '''
        Command \'volume export -incremental\' initiates an incremental export to a bucket.
        Indirectly tests VolumePlugin.export_volume() by observing call to volume service.

        Parameters
        ----------
        mockServiceGetVolume (unittest.mock.MagicMock)
        mockServiceExportVolume (unittest.mock.MagicMock)
        mockListTasks (unittest.mock.MagicMock)
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''

        # Using mock in python, top level packages (like argparse) cannot be patched outright.
        # http://stackoverflow.com/questions/22750555/python-mock-patch-top-level-packages
        # TODO: Test parse_args() directly.

        print("Plugin test: volume export -incremental")

        # Crucially, there is no -incremental specified.
        # Expected default value for that is False.
        args = ["volume", "export", "-volume_id=3", "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockServiceExportVolume.call_count == 1

        from_last_export = mockServiceExportVolume.call_args[0][5]
        assert from_last_export == False

        args = ["volume", "export", "-volume_id=3", "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com", "-incremental"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockServiceExportVolume.call_count == 2

        from_last_export = mockServiceExportVolume.call_args[0][5]
        assert from_last_export == True

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch("fdscli.services.abstract_service.AbstractService.get_url_preamble", side_effect=mock_get_url_preamble)
    @patch("fdscli.services.rest_helper.RESTHelper.post", side_effect=mock_post)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_service_incremental(self, mockServiceGetVolume, mockServicePost, mockUrlPreamble, mockListTasks, mockTabular, mockPretty):
        '''
        Command \'volume export -incremental\' initiates an incremental export to a bucket.
        Directly tests the real VolumeService.export_volume

        Parameters
        ----------
        mockServiceGetVolume (unittest.mock.MagicMock)
        mockServicePost (unittest.mock.MagicMock) : Replace REST helper post() with mock empty
        mockUrlPreamble (unittest.mock.MagicMock) : Returns the string to prepend for POST Url
        mockListTasks (unittest.mock.MagicMock)
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''
        volume = Volume();
        repo = Repository();
        repo.url = "https://s3.amazon.com"
        repo.bucket_name = "xvolrepo"
        repo.remote_om = None
        repo.credentials.access_key_id = "ABCDEFG"
        repo.credentials.secret_key = "/52/yrwhere"

        session = FdsAuth()
        service = VolumeService(session)
        service.export_volume(volume, repo, credential_digest="aaaa-bbbb", safeguard_preset=None, from_last_export=True)

        # The service export_volume is a url producer
        url = mockServicePost.call_args[0][1]
        assert mockServicePost.call_count == 1
        assert url == "http://localhost:7777/fds/config/v09/volumes/-1/exports/s3?incremental=true&named_credential_id=aaaa-bbbb"

        # Again, but using a snapshot_id=7
        service.export_volume(volume, repo, 7, safeguard_preset=None, from_last_export=True)

        # The service export_volume is a url producer
        url = mockServicePost.call_args[0][1]
        assert mockServicePost.call_count == 2
        assert url == "http://localhost:7777/fds/config/v09/volumes/-1/exports/s3?incremental=true&snapshot_id=7"

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch("fdscli.services.volume_service.VolumeService.export_volume", side_effect=mock_functions.exportVolume)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    @patch("fdscli.services.volume_service.VolumeService.get_safeguard_presets", side_effect=mock_functions.listSafeGuardPresets)
    def test_plugin_recurrence(self, mockListPresets, mockServiceGetVolume, mockServiceExportVolume, mockListTasks, mockTabular, mockPretty):
        '''
        Command \'volume export -safeguard_preset_id\' initiates a recurring export to a bucket.
        Indirectly tests VolumePlugin.export_volume() by observing call to volume service.
        The plugin is responsible for converting from SafeGuard preset Id to a SafeGuard policy.

        Parameters
        ----------
        :type mockListPresets: ``unittest.mock.MagicMock``
        :type mockServiceGetVolume: ``unittest.mock.MagicMock``
        :type mockServiceExportVolume: ``unittest.mock.MagicMock``
        :type mockListTasks: ``unittest.mock.MagicMock``
        :type mockTabular: ``unittest.mock.MagicMock``
        :type mockPretty: ``unittest.mock.MagicMock``
        '''

        # Using mock in python, top level packages (like argparse) cannot be patched outright.
        # http://stackoverflow.com/questions/22750555/python-mock-patch-top-level-packages
        # TODO: Test parse_args() directly.

        print("Plugin test: volume export -safeguard_preset_id")

        # Crucially, there is no -safeguard_preset_id specified.
        # Expected default value for that is False.
        args = ["volume", "export", "-volume_id=3", "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockServiceExportVolume.call_count == 1

        preset = mockServiceExportVolume.call_args[0][3]
        assert preset == None

        args = ["volume", "export", "-volume_id=3", "-safeguard_preset_id=1", "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com", "-incremental"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockServiceExportVolume.call_count == 2

        preset = mockServiceExportVolume.call_args[0][4]
        assert preset.id == 1

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch("fdscli.services.abstract_service.AbstractService.get_url_preamble", side_effect=mock_get_url_preamble)
    @patch("fdscli.services.rest_helper.RESTHelper.post", side_effect=mock_post)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_service_recurrence(self, mockServiceGetVolume, mockServicePost, mockUrlPreamble, mockListTasks, mockTabular, mockPretty):
        '''
        Command \'volume export -safeguard_preset_id\' initiates a recurring export to a bucket.
        Directly tests the real VolumeService.export_volume

        Parameters
        ----------
        mockServiceGetVolume (unittest.mock.MagicMock)
        mockServicePost (unittest.mock.MagicMock) : Replace REST helper post() with mock empty
        mockUrlPreamble (unittest.mock.MagicMock) : Returns the string to prepend for POST Url
        mockListTasks (unittest.mock.MagicMock)
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''
        volume = Volume();
        repo = Repository();
        repo.url = "https://s3.amazon.com"
        repo.bucket_name = "xvolrepo"
        repo.remote_om = None
        repo.credentials.access_key_id = "ABCDEFG"
        repo.credentials.secret_key = "/52/yrwhere"

        safeguard_preset = SafeGuardPreset()
        safeguard_preset.id = 2

        session = FdsAuth()
        service = VolumeService(session)
        service.export_volume(volume, repo, safeguard_preset=safeguard_preset, from_last_export=True)

        # The service export_volume is a url producer
        url = mockServicePost.call_args[0][1]
        assert mockServicePost.call_count == 1
        assert url == "http://localhost:7777/fds/config/v09/volumes/-1/exports/s3?incremental=true&safeguard_preset_id=2"
