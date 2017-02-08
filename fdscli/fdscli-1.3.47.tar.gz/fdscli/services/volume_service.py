# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

import json
from .abstract_service import AbstractService
from fdscli.model.fds_error import FdsError
from fdscli.utils.converters.common.repository_converter import RepositoryConverter
from fdscli.utils.converters.task.safeguard_task_converter import SafeGuardTaskConverter
from fdscli.utils.converters.volume.exported_volume_converter import ExportedVolumeConverter
from fdscli.utils.converters.volume.remote_volume_converter import RemoteVolumeConverter
from fdscli.utils.converters.volume.volume_converter import VolumeConverter
from fdscli.utils.converters.volume.snapshot_converter import SnapshotConverter
from fdscli.utils.converters.volume.preset_converter import PresetConverter

class VolumeService( AbstractService ):

    '''
    Created on Apr 3, 2015
    
    This class wraps all of the REST endpoints associated with volumes.  It "speaks" the volume model object
    and JSON and abstracts away all of the web protocols as a sort of volume SDK for FDS
    
    @author: nate
    '''
    
    def __init__(self, session):
        '''
        Parameters
        ----------
        :type session: ``services.FdsAuth``
        :param session: Data about the active session
        '''
        AbstractService.__init__(self, session)
            
    def find_volume_by_name(self, aName):  
        '''
        Get a volume by its name.  Hopefully this is temporary code only while the REST services
        don't support taking either the ID or the name.  Currently they only take a name.
        '''
        volumes = self.list_volumes()
        
        for volume in volumes:
            if ( volume.name == aName ):
                return volume  
    
    def list_volumes(self):
        
        '''
        Return the raw json list of volumes from the FDS REST call
        '''
        url = "{}{}".format( self.get_url_preamble(), "/volumes" )
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response

        volumes = []
        
        for j_volume in response:
            volume = VolumeConverter.build_volume_from_json( j_volume )
            volumes.append( volume )
            
        return volumes
    
    def get_volume(self, volume_id):
        ''' 
        get a single volume
        '''
        
        url = "{}{}{}".format( self.get_url_preamble(), "/volumes/", volume_id)
        response = self.rest_helper.get(self.session, url)
        
        if isinstance(response, FdsError):
            return response
        
        volume = VolumeConverter.build_volume_from_json(response) 
        return volume

    def export_volume(self, volume, repository, snapshot_id=0, credential_digest=None,
        safeguard_preset=None, from_last_export=False):
        '''
        Request export of serialized volume to read-only S3 repository.

        Parameters
        ----------
        volume (Volume) : A Volume object
        repository (Repository) : A Repository object that specifies credentials and
            storage endpoint

        snapshot_id (int) : Specified when user wishes to export an existing volume snapshot

        :type credential_digest: str
        :param credential_digest: Present if user supplies a named credential

        safeguard_preset (SafeGuardPreset) : preset named recurrence period
        from_last_export (Boolean) : True when export should start from a previous checkpoint

        Returns
        -------
        :type string or ``model.FdsError``
        :returns JSON formatted server response or error object
        '''
        url = "{}{}{}{}".format( self.get_url_preamble(), "/volumes/", volume.id, "/exports/s3")

        query_params = "?"
        num_params = 0

        if from_last_export:
            num_params += 1
            query_params = query_params + "incremental=true"

        if safeguard_preset != None:
            num_params += 1
            if num_params > 1:
                query_params = query_params + "&"
            query_params = query_params + "safeguard_preset_id=" + str(safeguard_preset.id)

        if snapshot_id != 0:
            num_params += 1
            if num_params > 1:
                query_params = query_params + "&"
            query_params = query_params + "snapshot_id=" + str(snapshot_id)

        if credential_digest is not None:
            if len( credential_digest ) != 0:
                num_params += 1
                if num_params > 1:
                    query_params = query_params + "&"
                query_params = query_params + "named_credential_id=" + credential_digest

        if num_params > 0:
            url = url + query_params

        data = RepositoryConverter.to_json( repository )
        j_response = self.rest_helper.post( self.session, url, data )
        return j_response

    def import_volume(self, volume_name, repository, credential_digest=None):
        '''
        Request import of serialized volume from existing S3 repository.

        Parameters
        ----------
        volume_name (str) : The name of the new volume
        repository (Repository) : A Repository object that specifies credentials and
            storage endpoint

        Returns
        -------
        The new volume name or instance of FdsError
        '''
        url = "{}{}".format( self.get_url_preamble(), "/volumes/imports/s3")
        query_params = "?"
        num_params = 0

        if credential_digest is not None:
            if len( credential_digest ) != 0:
                num_params += 1
                if num_params > 1:
                    query_params = query_params + "&"
                query_params = query_params + "named_credential_id=" + credential_digest

        if num_params > 0:
            url = url + query_params
        # Builds import volume request body
        d = dict()
        d["name"] = volume_name
        j_repository = RepositoryConverter.to_json( repository )
        d["repo"] = json.loads(j_repository)
        data = json.dumps(d)
        j_response = self.rest_helper.post( self.session, url, data )

        if isinstance(j_response, FdsError):
            return j_response

        return volume_name

    def list_exports_in_bucket(self, repository):
        '''
        List metadata for exported volumes in an existing bucket.

        Parameters
        ----------
        repository (Repository) : A Repository object that specifies credentials and
            storage endpoint

        Returns
        -------
        :type ``model.FdsError`` or list(``model.volume.ExportedVolume``)
        '''
        url = "{}{}".format( self.get_url_preamble(), "/volumes/exported/s3" )
        data = RepositoryConverter.to_json( repository )
        j_response = self.rest_helper.post( self.session, url, data )

        if isinstance(j_response, FdsError):
            return j_response

        exports = []

        for j_export in j_response:
            export = ExportedVolumeConverter.build_exported_volume_from_json( j_export )
            exports.append( export )

        return exports

    def create_volume(self, volume):
        '''
        Takes the passed in volume, converts it to JSON and uses the FDS REST
        endpoint to make the creation request
        '''
        url = "{}{}".format( self.get_url_preamble(), "/volumes" )
        data = VolumeConverter.to_json( volume )
        j_volume = self.rest_helper.post( self.session, url, data )

        if isinstance(j_volume, FdsError):
            return j_volume

        volume = VolumeConverter.build_volume_from_json( j_volume )
        return volume
    
    def clone_from_snapshot_id(self, volume, snapshot_id):
        ''' 
        clone from the given volume and snapshot ID
        '''
        url = "{}{}{}{}{}".format(self.get_url_preamble(), "/volumes/", volume.id, "/snapshot/", snapshot_id)
        data = VolumeConverter.to_json(volume)
        newVolume = self.rest_helper.post(self.session, url, data );
        
        if isinstance(newVolume, FdsError):
            return newVolume
        
        newVolume = VolumeConverter.build_volume_from_json(newVolume);
        return newVolume;
    
    def clone_from_timeline(self, volume, fromTime):
        '''
        Use a time and volume QoS settings to clone a new volume
        '''
        
        url = "{}{}{}{}{}".format( self.get_url_preamble(), "/volumes/", volume.id, "/time/", fromTime )
        data = VolumeConverter.to_json( volume )
        volume = self.rest_helper.post( self.session, url, data )

        if isinstance(volume, FdsError):
            return volume

        volume = VolumeConverter.build_volume_from_json( volume )
        return volume

    def clone_remote(self, remote_volume, snapshot_id=0, credential_digest=None, from_last_clone_remote=False):
        '''Request clone of volume here in remote domain

        Parameters
        ----------
        remote_volume (RemoteVolume) : Has OM service locator, name of volume from which clone
            is created, and settings and policies to apply to the newly created volume in the
            remote domain.
        snapshot_id (int) : Specified when user wishes to export an existing volume snapshot

        :type credential_digest: str
        :param credential_digest: Present if user supplies a named credential

        from_last_clone_remote (Boolean) : True when remote migration should start from a
            previous checkpoint

        Returns
        -------
        str: JSON formatted string
        '''
        url = "{}{}{}{}".format( self.get_url_preamble(), "/volumes/", remote_volume.volume.id, "/exports")

        query_params = "?"
        num_params = 0

        if from_last_clone_remote:
            num_params += 1
            query_params = query_params + "incremental=true"

        if snapshot_id != 0:
            num_params += 1
            if num_params > 1:
                query_params = query_params + "&"
            query_params = query_params + "snapshot_id=" + str(snapshot_id)

        if credential_digest is not None:
            if len( credential_digest ) != 0:
                num_params += 1
                if num_params > 1:
                    query_params = query_params + "&"
                query_params = query_params + "named_credential_id=" + credential_digest

        if num_params > 0:
            url = url + query_params

        data = RemoteVolumeConverter.to_json( remote_volume )
        j_response = self.rest_helper.post( self.session, url, data )
        return j_response

    def edit_volume(self, volume):
        '''
        Takes a volume formatted object and tries to make the edits
        to the volume it points to
        '''
        
        url = "{}{}{}".format( self.get_url_preamble(), "/volumes/", str(volume.id) )
        data = VolumeConverter.to_json( volume )
        j_volume = self.rest_helper.put( self.session, url, data )
        
        if isinstance(j_volume, FdsError):
            return j_volume
        
        volume = VolumeConverter.build_volume_from_json(j_volume)
        return volume
    
    def delete_volume(self, volume_id):
        '''
        Deletes a volume based on the volume name.  It expects this name to be unique
        '''
        
        url = "{}{}{}".format( self.get_url_preamble(), "/volumes/", volume_id )
        response = self.rest_helper.delete( self.session, url )
        
        if isinstance(response, FdsError):
            return response
        
        return response
    
    def create_snapshot(self, snapshot):
        '''
        Create a snapshot for the volume specified

        Returns
        -------
        :type ``model.FdsError`` or ``model.volume.Snapshot``
        '''
        
        url = "{}{}{}{}".format( self.get_url_preamble(), "/volumes/", snapshot.volume_id, "/snapshots" )
        data = SnapshotConverter.to_json(snapshot)
        response = self.rest_helper.post( self.session, url, data )

        if isinstance(response, FdsError):
            return response

        if ( response is not None and "uid" in response ):
            snapshot = SnapshotConverter.build_snapshot_from_json(response)
        #fi
        
        return snapshot
    
    def check_volume(self, volume_id, fix_flag=False ):
        '''
        Checks a specified volume. After sending, all it does is get the status.
        '''

        if fix_flag is False:
            print "check case"
            url = "{}{}{}{}".format( self.get_url_preamble(), "/volumes/", "check/", volume_id )
            response = self.rest_helper.get( self.session, url )
        else:
            print "fix case"
            url = "{}{}{}{}".format( self.get_url_preamble(), "/volumes/", "fix/", volume_id )
            response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response

        return response

    def fix_volume(self, volume_id):
        '''
        Fixes a specified volume. After sending, all it does is get the status.
        '''

        url = "{}{}{}{}".format( self.get_url_preamble(), "/volumes/", "fix/", volume_id )
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response

        return response
        
    def delete_snapshot(self, volume_id, snapshot_id):
        '''
        Delete a specific snapshot from a volume
        '''
        
        url = "{}{}{}{}{}".format( self.get_url_preamble(), "/volumes", volume_id, "/snapshot", snapshot_id )
        response = self.rest_helper.delete( url )
        
        if isinstance(response, FdsError):
            return response
        
        return response
    
    def list_snapshots(self, volume_id):
        '''
        Get a list of all the snapshots that exists for a given volume
        '''
        
        url = "{}{}{}{}".format ( self.get_url_preamble(), "/volumes/", volume_id, "/snapshots" )
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response
    
        snapshots = []
        
        for j_snapshot in response:
            snapshot = SnapshotConverter.build_snapshot_from_json( j_snapshot )
            snapshots.append( snapshot )
            
        return snapshots

    def list_safeguard_tasks_with_status(self):
        '''Request list of point-in-time status objects about data migration tasks.

        Each point-in-time status describes information about the task along with progress
        to completion.

        Returns
        -------
        :type ``model.FdsError`` or list(``model.task.SafeGuardTaskStatus``)
        '''
        url = "{}{}".format(self.get_url_preamble(), "/volumes/xport/tasks")
        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        tasks_with_status = []

        for j_task_status in response:
            task_with_status = SafeGuardTaskConverter.build_from_json(j_task_status)
            tasks_with_status.append(task_with_status)

        return tasks_with_status

    def replicate_snapshot(self, remote_volume, credential_digest, snapshot_id=0, from_last_clone_remote=True):
        '''Fires request to replicate snapshot to a remote domain.

        Performs an incremental export for the volume, then directs the replica volume to
        snapshot itself.

        Parameters
        ----------
        credential_digest (str)
        snapshot_id (int) : existing volume snapshot
        remote_volume (RemoteVolume) : Has OM service locator, name of volume from which clone
            is created, and settings and policies to apply to the newly created volume in the
            remote domain.
        from_last_clone_remote (Boolean) : True when remote migration should start from a
            previous checkpoint

        Returns
        -------
        str: JSON formatted string
        '''
        url = "{}{}{}{}{}{}".format( self.get_url_preamble(), "/volumes/", remote_volume.volume.id,
            "/replicate/snapshot/", snapshot_id, "/policy/0")

        query_params = "?"
        num_params = 0

        if from_last_clone_remote:
            num_params += 1
            query_params = query_params + "incremental=true"

        if snapshot_id != 0:
            num_params += 1
            if num_params > 1:
                query_params = query_params + "&"
            query_params = query_params + "snapshot_id=" + str(snapshot_id)

        if len( credential_digest ) != 0:
            num_params += 1
            if num_params > 1:
                query_params = query_params + "&"
            query_params = query_params + "named_credential_id=" + credential_digest

        if num_params > 0:
            url = url + query_params

        data = RemoteVolumeConverter.to_json( remote_volume )
        j_response = self.rest_helper.post( self.session, url, data )
        return j_response

    def get_data_protection_presets(self, preset_id=None):
        '''
        Get a list of timeline preset policies
        '''
        
        url = "{}{}".format( self.get_url_preamble(), "/presets/data_protection_policies")
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response
        
        presets = []
        
        for j_preset in response:
            
            if preset_id != None and int(j_preset["id"]) != int(preset_id):
                continue
            preset = PresetConverter.build_timeline_from_json( j_preset )
            presets.append( preset )
            
        return presets
    
    def get_qos_presets(self, preset_id=None):
        '''
        Get a list of QoS preset policies
        '''
        
        url = "{}{}".format( self.get_url_preamble(), "/presets/quality_of_service_policies" )
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response   
        
        presets = []
        
        for j_preset in response:
            
            if preset_id != None and int(j_preset["id"]) != int(preset_id):
                continue
            
            preset = PresetConverter.build_qos_preset_from_json( j_preset )
            presets.append( preset )
            
        return presets  

    def get_safeguard_presets(self, preset_id=None):
        '''
        Get a list of SafeGuard preset policies

        Parameters
        ----------
        :type preset_id: int
        :param preset_id: If specified, filter results list to match the given Id

        Returns
        -------
        :type ``model.FdsError`` or list(``model.volume.SafeGuardPreset``)
        '''
        url = "{}{}".format( self.get_url_preamble(), "/presets/safe_guard_policies" )
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response   

        presets = []
        # Serialize obj raw to json-encoded string
        #s = json.dumps(raw);
        # round-trip
        #response = json.loads(s);

        for j_preset in response:

            if preset_id != None and int(j_preset["uid"]) != int(preset_id):
                continue

            preset = PresetConverter.build_safeguard_preset_from_json( j_preset )
            presets.append( preset )

        return presets
