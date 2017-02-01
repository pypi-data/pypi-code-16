# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
from enum import Enum, unique
from fdscli.model.task.completion_status import CompletionStatus

@unique
class SafeGuardTaskType(Enum):
    unknown                       = 0
    # 'export' is deprecated, use export_s3_* instead
    export                        = 1
    # Server uses 'import', but that value is reserved in Python
    volume_import                 = 2
    # 'incremental' is deprecated, use export_replica_incremental instead
    incremental                   = 3
    # 'snapshot' is deprecated, use export_s3_snapshot or export_remoteclone_snapshot instead
    snapshot                      = 4
    export_remoteclone_checkpoint = 5
    export_remoteclone_snapshot   = 6
    export_replica_checkpoint     = 7
    export_replica_incremental    = 8
    export_s3_checkpoint          = 9
    export_s3_snapshot            = 10

    def __str__(self):
        '''
        Crucial for converting between json and this enum
        '''
        if self.value == SafeGuardTaskType.volume_import.value:
            return "import"
        return self.name

    @classmethod
    def getTableDisplayString(cls, enum_task_type):
        '''
        Returns
        -------
        :type str
        '''
        if enum_task_type.value == SafeGuardTaskType.volume_import.value:
            return "import"
        if enum_task_type.value == SafeGuardTaskType.export_remoteclone_checkpoint.value:
            return "volume copy"
        if enum_task_type.value == SafeGuardTaskType.export_remoteclone_snapshot.value:
            return "volume snapshot copy"
        if enum_task_type.value == SafeGuardTaskType.export_replica_checkpoint.value:
            return "volume replicate"
        if enum_task_type.value == SafeGuardTaskType.export_replica_incremental.value:
            return "volume incremental replicate"
        if enum_task_type.value == SafeGuardTaskType.export_s3_checkpoint.value:
            return "volume export"
        if enum_task_type.value == SafeGuardTaskType.export_s3_snapshot.value:
            return "volume snapshot export"
        return enum_task_type.name

class SafeGuardTaskStatus(object):
    '''A point-in-time status for a SafeGuard data migration task.

    Attributes
    ----------
    :type __uuid: string

    :type __description: string
    :attr __description: A description of the task

    :type __volume_id: int

    :type __status: ``model.task.CompletionStatus``

    :type __task_type: ``model.task.SafeGuardTaskType``

    :type __bucket_name: string
    :attr __bucket_name: For S3 export or S3 import, gives bucket name

    :type __endpoint: string
    :type __exported_name: string
    :attr __exported_name: remote volume name or S3 object prefix key

    :type __percent_complete: int
    :attr __percent_complete: estimate of completed data migration

    :type __error_type: string
    :type __error_text: string
    '''
    def __init__(self, uuid=-1, description=None, volume_id=-1, status=None,
        task_type=None, bucket_name=None, endpoint=None, exported_name=None, percent_complete=0,
        time_started=0, error_type=None, error_text=None):

        self.uuid = uuid
        self.description = description
        self.volume_id = volume_id
        self.status = status
        if self.status is None:
            self.status = CompletionStatus.unknown
        self.task_type = task_type
        if self.task_type is None:
            self.task_type = SafeGuardTaskType.unknown
        self.bucket_name = bucket_name
        self.endpoint = endpoint
        self.exported_name = exported_name
        self.percent_complete = percent_complete
        self.time_started = time_started
        self.error_type = error_type
        self.error_text = error_text

    @property
    def uuid(self):
        return self.__uuid

    @uuid.setter
    def uuid(self, uuid):
        self.__uuid = uuid

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description
 
    @property
    def bucket_name(self):
        return self.__bucket_name

    @bucket_name.setter
    def bucket_name(self, bucket_name):
        self.__bucket_name = bucket_name

    @property
    def endpoint(self):
        return self.__endpoint

    @endpoint.setter
    def endpoint(self, endpoint):
        self.__endpoint = endpoint

    @property
    def error_text(self):
        return self.__error_text

    @error_text.setter
    def error_text(self, error_text):
        self.__error_text = error_text

    @property
    def error_type(self):
        return self.__error_type

    @error_type.setter
    def error_type(self, error_type):
        self.__error_type = error_type

    @property
    def exported_name(self):
        return self.__exported_name

    @exported_name.setter
    def exported_name(self, exported_name):
        self.__exported_name = exported_name

    @property
    def percent_complete(self):
        return self.__percent_complete

    @percent_complete.setter
    def percent_complete(self, percent_complete):
        self.__percent_complete = int(percent_complete)

    @property
    def volume_id(self):
        return self.__volume_id

    @volume_id.setter
    def volume_id(self, volume_id):
        self.__volume_id = volume_id

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    @property
    def task_type(self):
        return self.__task_type

    @task_type.setter
    def task_type(self, task_type):
        self.__task_type = task_type

    @property
    def time_started(self):
        return self.__time_started

    @time_started.setter
    def time_started(self, time_started):
        self.__time_started = long(time_started)
