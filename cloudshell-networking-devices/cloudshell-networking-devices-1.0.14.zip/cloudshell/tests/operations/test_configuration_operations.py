from unittest import TestCase

import jsonpickle
from mock import MagicMock

from cloudshell.networking.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.shell.core.context import ResourceCommandContext, ReservationContextDetails, ResourceContextDetails
from cloudshell.shell.core.interfaces.save_restore import OrchestrationSavedArtifact


class TestConfigurationOperations(TestCase):

    def setUp(self):
        logger = MagicMock()
        api = MagicMock()
        context = ResourceCommandContext()
        context.resource = ResourceContextDetails()
        context.resource.name = 'resource_name'
        context.reservation = ReservationContextDetails()
        context.reservation.reservation_id = 'c3b410cb-70bd-4437-ae32-15ea17c33a74'
        context.resource.attributes = dict()
        context.resource.attributes['CLI Connection Type'] = 'Telnet'
        context.resource.attributes['Sessions Concurrency Limit'] = '1'
        self.handler = TestConfigurationRunnerImpl(api=api, logger=logger, context=context)

    def test_orchestration_save(self):
        request = """
        {
            "custom_params": {
                "folder_path" : "tftp://10.0.0.1/folder1",
                "vrf_management_name": "network-1"
                }
        }"""
        response = self.handler.orchestration_save(custom_params=request)
        decoded_response = jsonpickle.decode(response)
        self.assertIsNotNone(response)
        self.assertTrue('saved_artifacts_info' in decoded_response)
        self.assertIsNotNone(decoded_response['saved_artifacts_info'])
        self.assertTrue('saved_artifact' in decoded_response['saved_artifacts_info'])
        saved_artifact = decoded_response['saved_artifacts_info']['saved_artifact']
        self.assertIsNotNone(saved_artifact)
        self.assertTrue('artifact_type' in saved_artifact)
        self.assertIsNotNone(saved_artifact['artifact_type'])
        self.assertTrue(saved_artifact['artifact_type'] == 'test')
        self.assertTrue('identifier' in saved_artifact)
        self.assertIsNotNone(saved_artifact['identifier'])
        self.assertTrue(saved_artifact['identifier'] == 'identifier')

    def test_orchestration_restore(self):
        request = """
        {
        "saved_artifacts_info":
            {
            "saved_artifact":
                {
                "artifact_type": "test",
                "identifier": "identifier"
                },
            "resource_name": "resource_name",
            "restore_rules": {
                "requires_same_resource": true
                },
            "created_date": "2016-11-04T17:47:41.955000"
            }
        }"""
        self.handler.orchestration_restore(saved_artifact_info=request)


class TestConfigurationRunnerImpl(ConfigurationRunner):
    def save(self, folder_path, configuration_type, vrf_management_name=None):
        return OrchestrationSavedArtifact(identifier='identifier', artifact_type='test')

    def restore(self, path, configuration_type, restore_method, vrf_management_name=None):
        pass

    def __init__(self, logger, api, context):
        super(TestConfigurationRunnerImpl, self).__init__(logger, api, context)
