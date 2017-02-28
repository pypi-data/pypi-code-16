from typing import Union, Optional

from tornado.web import HTTPError

from talkzoho.projects.base_resource import BaseResource


class LogResource(BaseResource):

    def module_url(self, module_name):
        if self.component_type is None or self.component_type == 'general':
            return '{base_url}/portal/{portal_id}/projects/{project_id}/{module}/'.format(  # noqa
                base_url=self.service.base_url,
                portal_id=self.portal_id,
                project_id=self.project_id,
                module=module_name)
        else:
            return '{base_url}/portal/{portal_id}/projects/{project_id}/{component_type}/{component_id}/{module}/'.format(  # noqa
                base_url=self.service.base_url,
                portal_id=self.portal_id,
                project_id=self.project_id,
                component_type=self.component_type,
                component_id=self.component_id,
                module=module_name)

    async def get(self,
                  id: Union[int, str], *,
                  portal_id: Union[str, int],
                  project_id: Union[str, int],
                  component_type: Optional[str]=None,
                  columns=None):
        self.portal_id      = portal_id
        self.project_id     = project_id
        self.component_type = None

        log = await super().get(id=id, columns=columns)

        if component_type and log['component_type'] == component_type:
            raise HTTPError(404, 'No log with type {} found with that id. '
                                 'A {} log with that id does exist though.'.format(component_type, log['component_type']))  # noqa: E501

        return log

    async def filter(self, *,
                     portal_id: Union[str, int],
                     project_id: Union[str, int],
                     term: Optional[str]=None,
                     columns: Optional[list]=None,
                     offset: int=0,
                     limit: Optional[int]=None,
                     component_type: Optional[str]=None):
        self.portal_id      = portal_id
        self.project_id     = project_id
        self.component_type = None

        logs = await super().filter(term=term, columns=columns, offset=offset, limit=limit)  # noqa: E501

        if component_type:
            logs = [l for l in logs if l['component_type'] == component_type]

        return logs

    def _set_component_info(self, record: dict):
        if 'bug_id' in record and 'task_id' in record:
            raise AssertionError('A log entry can only be a general, bug or '
                                 'task. You appear to have passed both a bug '
                                 'and task id')
        elif 'bug_id' in record:
            self.component_id = record['bug_id']
            self.component    = 'bug'
        elif 'task_id' in record:
            self.component_id = record['task_id']
            self.component    = 'task'
        else:
            self.component    = 'general'

    async def insert(self, record: dict):
        self.portal_id  = record.pop('portal_id')
        self.project_id = record.pop('project_id')
        self._set_component_info(record)
        return await super().insert(record=record)

    async def update(self, record: dict):
        self.portal_id  = record.pop('portal_id')
        self.project_id = record.pop('project_id')
        self._set_component_info(record)
        return await super().update(record=record)

    async def delete(self,
                     id: Union[int, str],
                     *,
                     portal_id: Union[str, int],
                     project_id: Union[str, int],
                     bug_id: Optional[str]=None,
                     task_id: Optional[str]=None):
        self.portal_id  = portal_id
        self.project_id = project_id
        self._set_component_info({'bug_id': bug_id, 'task_id': task_id})
        return await super().delete(id=id)
