from test.base_cli_test import BaseCliTest
from boto.ec2.volume import Volume
import mock_functions
from mock import patch
from fdscli.model.common.size import Size
from fdscli.model.volume.settings.nfs_settings import NfsSettings
from fdscli.utils.fds_cli_configuration_manager import FdsCliConfigurationManager
from fdscli.utils.converters.volume.settings_converter import SettingsConverter

class TestNfsVolume( BaseCliTest ):
    '''
    Created on Nov 9, 2015
    
    @author: nate
    '''

    def test_marshalling(self):
        
        settings = NfsSettings()
        
        settings.use_acls = True
        settings.use_root_squash = False
        settings.synchronous = True
        
        settings.clients ="localhost*::[0-3]"

        settings.allow_mount = "false"
        settings.replica = "true"
        
        j_str = SettingsConverter.to_json(settings)
        
        print( j_str )
        
        m_settings = SettingsConverter.build_settings_from_json( j_str )
        
        assert m_settings.type == "NFS"
        assert m_settings.clients == "localhost*::[0-3]"
        assert m_settings.allow_mount == False
        assert m_settings.replica == True
        assert settings.use_acls is True
        assert settings.use_root_squash is False
        assert settings.synchronous is True
        
        # Checking the defaults
        assert settings.capacity != None, "Expected to have a capacity setting but found none."
        assert settings.capacity.size == 1, "Expected 1 but got {}".format( settings.capacity.size )
        assert settings.capacity.unit == "TB", "Expected TB as a size unit but got {}".format( settings.capacity.unit )
        
        settings.capacity = Size( size=3, unit="EB" )
        settings.use_acls = False
        
        j_str = SettingsConverter.to_json( settings )
        print( j_str )
        m_settings = SettingsConverter.build_settings_from_json(j_str)
        
        # Checking settings
        assert settings.capacity != None, "Expected to have a capacity setting but found none."
        assert settings.capacity.size == 3, "Expected 3 but got {}".format( settings.capacity.size )
        assert settings.capacity.unit == "EB", "Expected EB as a size unit but got {}".format( settings.capacity.unit )
        
        #make sure we're marshalling to the right version acls
        assert j_str.find( "noacl" ) != -1, "Expected to find 'noacl' in the string but did not."
        assert settings.use_acls is False
        
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "fdscli.services.volume_service.VolumeService.create_volume", side_effect=mock_functions.createVolume )        
    def test_nfs_creation(self, volumeCreate, listVolumes ):
        '''
        This test will make sure the settings look right after a volume create call
        '''
        print( "Testing NFS volume creation through the plugin with default size settings." )
        
        config = FdsCliConfigurationManager()
        self.cli.loadmodules()
        args = ['volume', 'create', 'nfs', '-name', 'nfs_max_ob_size', '-max_object_size', '2','-max_object_size_unit', 'MB']
        self.callMessageFormatter(args)
        self.cli.run(args)
        volume = volumeCreate.call_args[0][0]
        assert volume.settings.max_object_size.size == 2
        assert volume.settings.max_object_size.unit == 'MB'
        args = ['volume', 'create', 'nfs', '-name', 'nfs', '-acls', 'true', '-root_squash', 'false',
                '-clients', '128.*2*.[6-9]::ab']
         
        self.callMessageFormatter(args)
        self.cli.run(args)
         
        volume = volumeCreate.call_args[0][0]
        settings = volume.settings
     
        assert settings.type == 'NFS'
        assert settings.clients == "128.*2*.[6-9]::ab"
        # default max_object_size is 1 MB for NFS
        assert settings.max_object_size.size == 1048576
        assert settings.max_object_size.unit == 'B'
        assert settings.use_acls is True
        assert settings.use_root_squash is False
        assert settings.synchronous is False
        
        # Checking the defaults
        assert settings.capacity != None, "Expected to have a capacity setting but found none."
        assert settings.capacity.size == 524288, "Expected 524288 but got {}".format( settings.capacity.size )
        assert settings.capacity.unit == "GB", "Expected GB as a size unit but got {}".format( settings.capacity.unit )
        assert settings.allow_mount == True
        assert settings.replica == False

        print( "Testing NFS volume creation through the plugin with explicit size settings." )
        
        args = ['volume', 'create', 'nfs', '-name', 'nfs', '-acls', 'false', '-root_squash', 'true',
                '-clients', '228.*2*.[6-9]::ab', '-size', '243', '-size_unit', 'GB']
        
        self.callMessageFormatter(args)
        self.cli.run(args)
         
        volume = volumeCreate.call_args[0][0]
        settings = volume.settings
     
        assert settings.type == 'NFS'
        assert settings.clients == "228.*2*.[6-9]::ab"
        assert settings.use_acls is False
        assert settings.use_root_squash is True
        assert settings.synchronous is False
        
        # Checking the defaults
        assert settings.capacity != None, "Expected to have a capacity setting but found none."
        assert settings.capacity.size == 243, "Expected 243 but got {}".format( settings.capacity.size )
        assert settings.capacity.unit == "GB", "Expected GB as a size unit but got {}".format( settings.capacity.unit )
        
    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getNfsVolume)
    @patch( "fdscli.services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "fdscli.services.volume_service.VolumeService.edit_volume", side_effect=mock_functions.editVolume )                 
    def test_nfs_edit(self, mock_edit, mock_list, mock_get_vol):
        '''
        This test will try to edit an NFS Volume
        '''
        
        print( "Testing the editing of an NFS volume" )
        
        config = FdsCliConfigurationManager()
        
        self.cli.loadmodules()
        
        args = ['volume', 'edit', '-volume_id', '3', '-clients', '10.1.1.1']
        
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        volume = mock_edit.call_args[0][0]
        settings = volume.settings
        
        assert volume.id == 3
        assert settings.clients == '10.1.1.1'
