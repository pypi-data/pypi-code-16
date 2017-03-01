# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import collections
import json
from fdscli.model.fds_error import FdsError
from fdscli.services.abstract_service import AbstractService
from fdscli.utils.converters.task.safeguard_task_converter import SafeGuardTaskConverter

class SafeGuardTaskClient(AbstractService):
    '''
    Formation SafeGuardTask
    Formation SafeGuardTask is a web service that enables client code to monitor and interact
    with SafeGuard tasks.

    Client
    This low-level API provides one-to-one mappings to the underlying HTTP API operations.
    '''

    def __init__(self, session):
        '''
        :type session: ``services.FdsAuth``
        :param session: Data about the active session
        '''
        AbstractService.__init__(self, session)

    def cancel_safeguard_task(self, task_uuid):
        '''Request to cancel an existing SafeGuard task.
        '''
        url = "{}{}{}".format( self.get_url_preamble(), "/safeguard/tasks/", task_uuid)
        d = dict()
        data = json.dumps(d)

        j_response = self.rest_helper.put( self.session, url, data )
        return j_response

    def list_tasks(self, url):
        '''Request list of point-in-time status objects about data migration tasks.

        Each point-in-time status describes information about the task along with progress
        to completion.

        Parameters
        ----------
        :type url: str

        Returns
        -------
        :type ``model.FdsError`` or list(``model.task.SafeGuardTaskStatus``)
        '''
        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        tasks_with_status = []

        for j_task_status in response:
            task_with_status = SafeGuardTaskConverter.build_from_json(j_task_status)
            tasks_with_status.append(task_with_status)

        return tasks_with_status

    def get_task(self, task_id):
        '''Request point-in-time status for a data migration task.

        Parameters
        ----------
        :type task_id: str

        Returns
        -------
        :type ``model.FdsError`` or ``model.task.SafeGuardTaskStatus``
        '''
        url = "{}{}{}".format(self.get_url_preamble(), "/safeguard/tasks/", task_id)

        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        task_with_status = SafeGuardTaskConverter.build_from_json(response)

        return task_with_status

    def list_tasks_by_snapshot(self, snapshot_id):
        '''Request list of point-in-time status objects about data migration tasks.

        Filters according to given snapshot Id.
        Each point-in-time status describes information about the task along with progress
        to completion.

        Returns
        -------
        :type ``model.FdsError`` or list(``model.task.SafeGuardTaskStatus``)
        '''
        url = "{}{}{}{}".format(self.get_url_preamble(), "/snapshots/", snapshot_id, "/safeguard/tasks")
        return self.list_tasks(url)

    def list_tasks_by_volume(self, volume_id):
        '''Request list of point-in-time status objects about data migration tasks.

        Filters according to given volume Id.
        Each point-in-time status describes information about the task along with progress
        to completion.

        Returns
        -------
        :type ``model.FdsError`` or list(``model.task.SafeGuardTaskStatus``)
        '''
        url = "{}{}{}{}".format(self.get_url_preamble(), "/volumes/", volume_id, "/safeguard/tasks")
        return self.list_tasks(url)

    def list_tasks_with_status(self):
        '''Request list of point-in-time status objects about data migration tasks.

        Each point-in-time status describes information about the task along with progress
        to completion.

        Returns
        -------
        :type ``model.FdsError`` or list(``model.task.SafeGuardTaskStatus``)
        '''
        url = "{}{}".format(self.get_url_preamble(), "/safeguard/tasks")
        return self.list_tasks(url)
