from typing import Union, Optional

from talkzoho.projects.base_resource import BaseResource


class ProjectResource(BaseResource):

    def module_url(self, module_name):
        return '{base_url}/portal/{portal_id}/projects/{project_id}/{module}/'.format(  # noqa
            base_url=self.service.base_url,
            portal_id=self.portal_id,
            project_id=self.project_id,
            module=module_name)

    async def get(self,
                  id: Union[int, str], *,
                  portal_id: Union[str, int],
                  project_id: Union[str, int],
                  columns=None):
        self.portal_id = portal_id
        self.project_id = project_id
        return await super().get(id=id, columns=columns)

    async def filter(self, *,
                     portal_id: Union[str, int],
                     project_id: Union[str, int],
                     term: Optional[str]=None,
                     columns: Optional[list]=None,
                     offset: int=0,
                     limit: Optional[int]=None):
        self.portal_id  = portal_id
        self.project_id = project_id
        return await super().filter(
            term=term,
            columns=columns,
            offset=offset,
            limit=limit)

    async def insert(self, record: dict):
        self.portal_id  = record.pop('portal_id')
        self.project_id = record.pop('project_id')
        return await super().insert(record=record)

    async def update(self, record: dict):
        self.portal_id  = record.pop('portal_id')
        self.project_id = record.pop('project_id')
        return await super().update(record=record)

    async def delete(self,
                     id: Union[int, str],
                     *,
                     portal_id: Union[str, int],
                     project_id: Union[str, int]):
        self.portal_id  = portal_id
        self.project_id = project_id
        return await super().delete(id=id)
