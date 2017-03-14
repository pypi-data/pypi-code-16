# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from fdscli.model.volume.volume import Volume

class RemoteVolume( object ):
    '''Used to form a volume clone request where the clone is created in the domain indicated
    by the OM service locator.

    Unlike a volume, no corresponding object is persisted in the local domain.

    Attributes
    ----------
    __remote_om_url (str): OM service locator, like 'https://username.password@omHostName.omPort'
    __source_volume_name (str): Name of the volume from which remote clone is made
    __volume (Volume): Settings and policies applied when creating remote clone
    '''
    def __init__(self, volume=None, remote_om_url=None, source_volume_name=None):

        self.__remote_om_url = remote_om_url
        self.__source_volume_name = source_volume_name
        self.__volume = volume
        if self.__volume is None:
            self.__volume = Volume()

    @property
    def remote_om_url(self):
        return self.__remote_om_url

    @remote_om_url.setter
    def remote_om_url(self, remote_om_url):
        self.__remote_om_url = remote_om_url

    @property
    def source_volume_name(self):
        return self.__source_volume_name

    @source_volume_name.setter
    def source_volume_name(self, source_volume_name):
        self.__source_volume_name = source_volume_name

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, volume):
        self.__volume = volume

