# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.volume.recurrence_rule import RecurrenceRule

class Subscription(object):
    '''Controls data migration for a volume for a given recurrence rule.

    Attributes
    ----------
    :type __digest: string
    :attr __digest: Hash value that uniquely identifies the subscription

    :type __name: string
    :attr __name: Customer assigned or machine assigned name, unique for a given tenant

    :type __volume_id: int
    :attr __volume_id: Unique volume identifier

    :type __recurrence_rule: ``model.volume.RecurrenceRule``
    :attr __recurrence_rule: Defines a recurrence rule for data migration

    :type __creation_time: int
    :attr __creation_time: A timestamp in epoch seconds

    :type __remote_volume: string
    :attr __remote_volume: If the data migration is a remote clone, this gives the remote volume name

    :type __named_credential: ``model.common.NamedCredential`` 
    _attr __named_credential: A named credential that gives endpoint
    '''

    def __init__(self, digest=None, name=None, volume_id=None, creation_time=0,
         recurrence_rule=None, remote_volume=None, named_credential=None):

        self.digest = digest
        self.name = name
        self.volume_id = volume_id
        self.creation_time = creation_time
        self.recurrence_rule = recurrence_rule
        if self.recurrence_rule is None:
            self.recurrence_rule = RecurrenceRule()
        self.remote_volume = remote_volume
        self.named_credential = named_credential
        if self.named_credential is None:
            self.named_credential = NamedCredential()

    @property
    def digest(self):
        return self.__digest

    @digest.setter
    def digest(self, digest):
        self.__digest = digest

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name
 
    @property
    def volume_id(self):
        return self.__volume_id

    @volume_id.setter
    def volume_id(self, volume_id):
        self.__volume_id = volume_id

    @property
    def creation_time(self):
        return self.__creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        self.__creation_time = creation_time

    @property
    def recurrence_rule(self):
        return self.__recurrence_rule

    @recurrence_rule.setter
    def recurrence_rule(self, recurrence_rule):
        self.__recurrence_rule = recurrence_rule

    @property
    def remote_volume(self):
        return self.__remote_volume

    @remote_volume.setter
    def remote_volume(self, remote_volume):
        self.__remote_volume = remote_volume

    @property
    def named_credential(self):
        return self.__named_credential

    @named_credential.setter
    def named_credential(self, named_credential):
        self.__named_credential = named_credential
