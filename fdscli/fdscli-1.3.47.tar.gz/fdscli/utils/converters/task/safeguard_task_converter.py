# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.task.completion_status import CompletionStatus
from fdscli.model.task.safeguard_task_status import SafeGuardTaskStatus, SafeGuardTaskType
from fdscli.utils.converters.common.optional_string_converter import OptionalStringConverter

class SafeGuardTaskConverter(object):
    '''Helper class for marshalling between SafeGuardTaskStatus and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json_string(task_with_status):
        '''Converts ``model.task.SafeGuardTaskStatus`` object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type task_with_status: ``model.task.SafeGuardTaskStatus`` object

        Returns
        -------
        :type string
        '''
        d = dict()

        d["uuid"] = task_with_status.uuid
        d["description"] = task_with_status.description
        d["volume_id"] = int(task_with_status.volume_id)
        d["completionState"] = str(task_with_status.status)
        d["type"] = str(task_with_status.task_type)
        if task_with_status.bucket_name is not None:
            d1 = dict()
            d1['value'] = task_with_status.bucket_name
            d['bucketName'] = json.dumps( d1 )
        if task_with_status.endpoint is not None:
            d["endpoint"] = task_with_status.endpoint
        if task_with_status.exported_name is not None:
            d["exportedName"] = task_with_status.exported_name
        d["percentComplete"] = int(task_with_status.percent_complete)

        ctime = dict()
        ctime["seconds"] = task_with_status.time_started
        ctime["nanos"] = 0
        d["timeStarted"] = ctime

        if task_with_status.error_type is not None:
            d['errorType'] = task_with_status.error_type
        if task_with_status.error_text is not None:
            d['errorText'] = task_with_status.error_text

        result = json.dumps(d)
        return result;

    @staticmethod
    def build_from_json(j_str):
        '''Produce a ``model.task.SafeGuardTaskStatus`` object from deserialized server response

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.task.SafeGuardTaskStatus``
        '''
        task_with_status = SafeGuardTaskStatus()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)

        # {
        #     'estimatedCompletionTime': {
        #         'seconds': '1483637605',
        #         'nanos': 979000000
        #     },
        #     'xdiTaskUUID': '643ebefe-f096-4799-91ed-0f794a1c1f00',
        #     'uuid': 'fcef4471-ff42-4546-89e3-e90b759ecf74',
        #     'endpoint': 'http://localhost',
        #     'description': 'Task type: S3_FULL_EXPORT, status: FAILED, % complete: NaN',
        #     'retries': 0,
        #     'sequenceId': '0',
        #     'userId': '1',
        #     'volumeId': '3',
        #     'tenantId': '0',
        #     'exportedName': '2/0/3/0/2017-01-05T17:33:21',
        #     'subscriptionDigest': {},
        #     'cloneName': '2/0/3/0/2017-01-05T17:33:21',
        #     'percentComplete': 100,
        #     'namedCredentialDigest': {},
        #     'originalName': 'vol1',
        #     'snapshotId': '0',
        #     'metadata': {
        #         'customMetadata': {
        #             'originalVolumeName': 'vol1'
        #         }
        #     },
        #     'type': 'EXPORT_S3_CHECKPOINT',
        #     'completionState': 'ABANDONED',
        #     'timeStarted': {
        #         'seconds': '1483637602',
        #         'nanos': 820000000
        #     }
        # }

        task_with_status.uuid = j_str.pop("uuid", task_with_status.uuid)
        task_with_status.volume_id = int(j_str.pop("volumeId", task_with_status.volume_id))
        if "description" in j_str:
            task_with_status.description = j_str.pop("description", task_with_status.description)
        status_str = j_str.pop("completionState", "unknown")
        for s in CompletionStatus:
            if str(s) == str(status_str.lower()):
                task_with_status.status = s
                break

        type_str = j_str.pop("type", "unknown")
        for t in SafeGuardTaskType:
            if str(t) == str(type_str.lower()):
                task_with_status.task_type = t
                break

        if "bucketName" in j_str:
            # TODO: bucketName is a json object because of Java Optional - fix the response
            bucket_name = OptionalStringConverter.build_from_json(j_str.pop("bucketName"))
            if bucket_name is not None and len(bucket_name) > 0:
                task_with_status.bucket_name = bucket_name

        if "endpoint" in j_str:
            task_with_status.endpoint = j_str.pop("endpoint", task_with_status.endpoint)

        if "exportedName" in j_str:
            task_with_status.exported_name = j_str.pop("exportedName", task_with_status.exported_name)

        if "percentComplete" in j_str:
            task_with_status.percent_complete = int(j_str.pop("percentComplete", task_with_status.percent_complete))

        if 'timeStarted' in j_str:
            ctime = j_str.pop('timeStarted', task_with_status.time_started)
            task_with_status.time_started = ctime['seconds']

        if 'errorType' in j_str:
            task_with_status.error_type = j_str.pop('errorType', task_with_status.error_type)
        if 'errorText' in j_str:
            task_with_status.error_text = j_str.pop('errorText', task_with_status.error_text)

        return task_with_status
