from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions

class TestVolumePresets(BaseCliTest):
    '''
    Created on May 7, 2015
    
    @author: nate
    '''
    @patch( "fdscli.services.volume_service.VolumeService.get_qos_presets", side_effect=mock_functions.listQosPresets)
    @patch( "fdscli.services.volume_service.VolumeService.get_data_protection_presets", side_effect=mock_functions.listTimelinePresets)
    @patch( "fdscli.services.volume_service.VolumeService.get_safeguard_presets", side_effect=mock_functions.listSafeGuardPresets)
    def test_list_presets(self, mockListSafeGuardPresets, mockTime, mockQos):
        '''
        Test whether our preset listing works

        Parameters
        ----------
        mockListSafeGuardPresets (unittest.mock.MagicMock)
        mockTime (unittest.mock.MagicMock)
        mockQos (unittest.mock.MagicMock)
        '''

        args = ["presets","list"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockTime.call_count == 1
        assert mockListSafeGuardPresets.call_count == 1
        assert mockQos.call_count == 1

        args = ["presets","list", "-type=timeline"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockTime.call_count == 2
        assert mockListSafeGuardPresets.call_count == 1
        assert mockQos.call_count == 1

        args = ["presets","list", "-type=qos"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockTime.call_count == 2
        assert mockListSafeGuardPresets.call_count == 1
        assert mockQos.call_count == 2

        args = ["presets","list", "-type=safeguard"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockTime.call_count == 2
        assert mockListSafeGuardPresets.call_count == 2
        assert mockQos.call_count == 2

    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes)
    @patch( "fdscli.services.volume_service.VolumeService.get_qos_presets", side_effect=mock_functions.listQosPresets)
    @patch( "fdscli.services.volume_service.VolumeService.create_volume", side_effect=mock_functions.createVolume)
    def test_create_volume_with_qos(self, mockCreate, mockQos, mockList):     
        '''
        Try to create a volume using a qos preset
        '''
        
        args = ["volume","create", "object", "-name=Test", "-qos_preset_id=1"]
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert mockCreate.call_count == 1
        assert mockQos.call_count == 1
        
        volume = mockCreate.call_args[0][0]
        preset_id = mockQos.call_args[1]["preset_id"]
        
        assert preset_id == "1"
        
        assert volume.qos_policy.priority == 1
        assert volume.qos_policy.iops_min == 1
        assert volume.qos_policy.iops_max == 1
    
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.create_snapshot_policy", side_effect=mock_functions.createSnapshotPolicy)
    @patch( "fdscli.services.volume_service.VolumeService.get_data_protection_presets", side_effect=mock_functions.listTimelinePresets)
    @patch( "fdscli.services.volume_service.VolumeService.get_qos_presets", side_effect=mock_functions.listQosPresets)
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_timeline", side_effect=mock_functions.cloneFromTimelineTime)   
    def test_clone_volume(self, mockClone, mockFind, mockQos, mockTimeline, mockCreatePolicy, mockList):
        '''
        Test cloning a volume with both a timeline preset and a qos preset
        '''
        
        args = ["volume", "clone", "-volume_id=100", "-name=cloned", "-qos_preset_id=1", "-data_protection_preset_id=1"]
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert mockFind.call_count == 1
        assert mockQos.call_count == 1
        assert mockTimeline.call_count == 1
        assert mockClone.call_count == 1
        assert mockCreatePolicy.call_count == 0
        assert mockList.call_count == 1
        
        vol_id = mockFind.call_args[0][0]
        assert vol_id == "100"
        
        volume = mockClone.call_args[0][0]
        assert volume.qos_policy.priority == 1
        assert volume.qos_policy.iops_min == 0
        assert volume.qos_policy.iops_max == 0
        
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.create_snapshot_policy", side_effect=mock_functions.createSnapshotPolicy)
    @patch( "fdscli.services.volume_service.VolumeService.get_data_protection_presets", side_effect=mock_functions.listTimelinePresets)
    @patch( "fdscli.services.volume_service.VolumeService.get_qos_presets", side_effect=mock_functions.listQosPresets)
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.volume_service.VolumeService.edit_volume", side_effect=mock_functions.editVolume)           
    def test_edit_volume_with_presets(self, mockEdit, mockFind, mockQos, mockTimeline, mockCreatePolicy, mockList):
        '''
        Test editing a volume by sending in some preset selections
        '''
        
        args = ["volume", "edit", "-volume_id=100", "-qos_preset_id=1", "-data_protection_preset_id=1"]
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert mockFind.call_count == 1
        assert mockQos.call_count == 1
        assert mockTimeline.call_count == 1
        assert mockEdit.call_count == 1
        assert mockCreatePolicy.call_count == 0
        assert mockList.call_count == 1
        
        vol_id = mockFind.call_args[0][0]
        assert vol_id == "100"
        
        volume = mockEdit.call_args[0][0]
        assert volume.qos_policy.priority == 1
        assert volume.qos_policy.iops_min == 1
        assert volume.qos_policy.iops_max == 1
        
        assert vol_id == "100"
        assert vol_id == "100"        

