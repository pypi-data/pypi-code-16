# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#

from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.volume.remote_volume import RemoteVolume
from fdscli.model.volume.volume import Volume
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.volume_service import VolumeService
from fdscli.utils.converters.volume.volume_converter import VolumeConverter
from fdscli.utils.converters.volume.remote_volume_converter import RemoteVolumeConverter

def mock_post( session, url, data ):
    print url

def mock_get_url_preamble():
    return "http://localhost:7777/fds/config/v09"

class VolumeCloneTest( BaseCliTest):
    '''
    Created on Apr 23, 2015
    
    Test out the clone calls
    
    @author: nate
    '''
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)    
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_snapshot_id", side_effect=mock_functions.cloneFromSnapshotId)
    def test_clone_from_snapshot_id(self, mockCloneSnap, mockList, mockGet ):
        '''
        Try to create a clone with a snapshot ID
        '''
        
        print("Trying to create a volume clone by snapshot ID and defaults")

        args = ["volume", "clone", "-volume_id=1", "-snapshot_id=35", "-name=CloneVol"]
        
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockCloneSnap.call_count == 1
        assert mockList.call_count == 1
        
        snap_id = mockCloneSnap.call_args[0][1]
        volume = mockCloneSnap.call_args[0][0]
        
        assert snap_id == "35"
        assert volume.name == "CloneVol"
        
        print("Clone volume by snapshot ID was successful.\n\n")

    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_timeline", side_effect=mock_functions.cloneFromTimelineTime )
    def test_clone_from_timeline_name(self, mockClone, mockList, mockId ):
        '''
        Test creating a clone from the timeline with a volume name
        '''
        
        print("Trying to clone a volume from a timeline time and a volume name")

        args = ["volume", "clone", "-time=123456789", "-volume_id=MyVol", "-name=ClonedVol"]
        
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockClone.call_count == 1
        assert mockList.call_count == 1

        assert mockId.call_count == 1
        
        a_time = mockClone.call_args[0][1]
        assert a_time == 123456789
        volume = mockClone.call_args[0][0]
        assert volume.name == "ClonedVol"
        
        print("Cloning from timeline time and volume name was successful.\n\n")

    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_timeline", side_effect=mock_functions.cloneFromTimelineTime )
    def test_clone_from_timeline_id(self, mockClone, mockList, mockId ):
        '''
        Test creating a clone from the timeline with a volume ID
        '''
        
        print("Trying to clone a volume from a timeline time and a volume ID")

        args = ["volume", "clone", "-time=123456789", "-volume_id=13", "-name=ClonedVol2"]
        
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockClone.call_count == 1
        assert mockList.call_count == 1
        assert mockId.call_count == 1
        
        an_id = mockId.call_args[0][0]
        assert an_id == "13"
        
        a_time = mockClone.call_args[0][1]
        assert a_time == 123456789
        volume = mockClone.call_args[0][0]
        assert volume.name == "ClonedVol2"
        
        print("Cloning from timeline time and volume name was successful.\n\n")

    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)      
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_timeline", side_effect=mock_functions.cloneFromTimelineTime )        
    def test_clone_from_args(self, mockClone, mockList, mockGet ):
        '''
        Test to see if new QoS items are passed through from the arg list
        '''
        
        print("Trying to create a clone with different QoS settings")

        args = ["volume", "clone", "-volume_id=FirstVol", "-name=ClonedVol", "-priority=9", "-iops_min=5000",
                "-iops_max=3000", "-continuous_protection=86500"]
        
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockClone.call_count == 1
        assert mockList.call_count == 1
        
        a_time = mockClone.call_args[0][1]
        volume = mockClone.call_args[0][0]

        assert volume.qos_policy.priority == 9
        assert volume.qos_policy.iops_min == 5000
        assert volume.qos_policy.iops_max == 3000
        assert volume.data_protection_policy.commit_log_retention == 86500
        assert volume.media_policy == "HYBRID"
        assert a_time == 0
        
        print("Cloning volume with new QoS settings from args was successful.\n\n")

    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch("fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes)
    @patch("fdscli.services.volume_service.VolumeService.clone_from_timeline",
           side_effect=mock_functions.cloneFromTimelineTime)
    def test_clone_from_args_change_media_policy(self, mockClone, mockList, mockGet):
        '''
        Test to see if new QoS items are passed through from the arg list
        '''

        print("Trying to create a clone with different tiering settings")

        args = ["volume", "clone", "-volume_id=FirstVol", "-name=ClonedVol", "-priority=9", "-iops_min=5000",
                "-iops_max=3000", "-continuous_protection=86500", "-tiering_policy=SSD"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockClone.call_count == 1
        assert mockList.call_count == 1

        a_time = mockClone.call_args[0][1]
        volume = mockClone.call_args[0][0]

        assert volume.qos_policy.priority == 9
        assert volume.qos_policy.iops_min == 5000
        assert volume.qos_policy.iops_max == 3000
        assert volume.data_protection_policy.commit_log_retention == 86500
        assert volume.media_policy == "SSD"
        assert a_time == 0

        print("Cloning volume with new tiering settings from args was successful.\n\n")

    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)        
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_timeline", side_effect=mock_functions.cloneFromTimelineTime )        
    def test_clone_from_data(self, mockClone, mockList, mockGet ):
        '''
        Test to see if new QoS settings are accepted from a JSON data string
        '''
        
        print("Trying to clone a volume with different QoS settings from JSON string")

        volume = Volume()
        volume.qos_policy.iops_min = 30000
        volume.qos_policy.iops_max = 100500
        volume.qos_policy.priority = 1
        volume.data_protection_policy.commit_log_retention = 90000
        
        volStr = VolumeConverter.to_json( volume )
        
        args = ["volume", "clone", "-volume_id=MyVol", "-data=" + volStr, "-name=ClonedVol7"]
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockClone.call_count == 1
        assert mockList.call_count == 1
        
        a_time = mockClone.call_args[0][1]
        volume = mockClone.call_args[0][0]
        
        # 0 = now 
        assert a_time == 0
        assert volume.qos_policy.iops_min == 30000
        assert volume.qos_policy.iops_max == 100500
        assert volume.qos_policy.priority == 1
        assert volume.data_protection_policy.commit_log_retention["seconds"] == 90000
        
        print("Cloning volume with new QoS setting from a JSON string was successful.")

    @patch( "fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    @patch( "fdscli.services.volume_service.VolumeService.get_data_protection_presets", side_effect=mock_functions.listTimelinePresets)
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)
    @patch( "fdscli.services.volume_service.VolumeService.clone_remote", side_effect=mock_functions.cloneRemote)
    def test_clone_remote(self, mockCloneRemote, mockId, mockTimelinePresets, mockListTasks):
        '''
        Test creating a clone in a remote domain
        '''

        print("Trying to clone a volume from a timeline time and a volume name to a remote domain")

        args = ["volume", "clone", "-time=123456789", "-volume_id=MyVol", "-name=ClonedVol",
            "-remote_om=https://admin:admin@localhost:7777"]
        
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockCloneRemote.call_count == 1
        assert mockId.call_count == 1

        remote_volume = mockCloneRemote.call_args[0][0]
        j_remote_volume = RemoteVolumeConverter.to_json(remote_volume)
        print j_remote_volume

        # The mock returns "VolumeName"
        assert remote_volume.source_volume_name == "VolumeName"
        assert remote_volume.remote_om_url == "https://admin:admin@localhost:7777"
        assert remote_volume.volume.name == "ClonedVol"

        from_last_clone_remote = mockCloneRemote.call_args[0][1]
        assert from_last_clone_remote == False

        # Now try an incremental clone

        args = ["volume", "clone", "-snapshot_id=123456789", "-volume_id=MyVol", "-name=ClonedVol",
            "-remote_om=https://admin:admin@localhost:7777", "-incremental"]

        self.callMessageFormatter(args)
        self.cli.run( args )
        assert mockCloneRemote.call_count == 2
        from_last_clone_remote = mockCloneRemote.call_args[0][3]
        assert from_last_clone_remote == True

        print("Cloning to remote was successful.\n\n")

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.abstract_service.AbstractService.get_url_preamble", side_effect=mock_get_url_preamble)
    @patch("fdscli.services.rest_helper.RESTHelper.post", side_effect=mock_post)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_service_clone_remote(self, mock_get_volume, mock_post, mock_url, mock_write, mock_pretty):
        '''Directly tests the real VolumeService.clone_remote.
        '''
        snapshot_id = 365L
        credential_digest = "aaaa-bbbb"
        remote_volume = RemoteVolume()
        session = FdsAuth()
        service = VolumeService(session)
        service.clone_remote(remote_volume, snapshot_id, credential_digest, from_last_clone_remote=False)

        # The service clone_remote is a url producer
        url = mock_post.call_args[0][1]
        assert mock_post.call_count == 1
        assert url == "http://localhost:7777/fds/config/v09/volumes/-1/exports?snapshot_id=365&named_credential_id=aaaa-bbbb"

    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById)        
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_timeline", side_effect=mock_functions.cloneFromTimelineTime )
    @patch( "fdscli.services.volume_service.VolumeService.clone_from_snapshot_id", side_effect=mock_functions.cloneFromSnapshotId)
    def test_boundary_conditions(self, mockSnap, mockTime, mockGet):
        '''
        Test the expected failure cases if arguments are out of bounds
        '''
        
        print("Testing boundary conditions on the arguments")

        args = ["volume", "clone", "-priority=9", "-iops_guarantee=1000", "-iops_limit=3000", "-continuous_protection=86700", "-name=NewVol"]
        
        print("Testing need for volume_id, snapshot_id or volume_name")

        self.callMessageFormatter(args)
        self.cli.run( args )
        assert mockSnap.call_count == 0
        assert mockTime.call_count == 0
        
        args.append( "-volume_id=35")
        self.callMessageFormatter(args)
        self.cli.run( args )
        assert mockSnap.call_count == 0
        assert mockTime.call_count == 0
                
        print("Testing bad priority")

        args[2] = "-priority=11"      
        self.callMessageFormatter(args)
        self.cli.run( args )
        assert mockSnap.call_count == 0
        assert mockTime.call_count == 0
        
        print("Testing bad iops_guarantee")

        args[2] = "-priority=1"
        args[3] = "-iops_guarantee=-1"
        self.callMessageFormatter(args)
        self.cli.run( args )
        assert mockSnap.call_count == 0
        assert mockTime.call_count == 0
        
        print("Testing bad iops_limit")

        args[3] = "-iops_guarantee=4000"
        args[4] = "-iops_limit=100000"
        self.callMessageFormatter(args)
        self.cli.run( args )
        assert mockSnap.call_count == 0
        assert mockTime.call_count == 0
        
        print("Testing bad continuous protection")

        args[4] = "-iops_limit=1000"
        args[5] = "-continuous_protection=1000"
        self.callMessageFormatter(args)
        self.cli.run( args )
        assert mockSnap.call_count == 0
        assert mockTime.call_count == 0
