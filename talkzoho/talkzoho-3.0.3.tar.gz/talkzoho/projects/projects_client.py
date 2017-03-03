from talkzoho.service_client import ServiceClient
from talkzoho.projects.base_resource import BaseResource
from talkzoho.projects.portal_resource import PortalResource
from talkzoho.projects.project_resource import ProjectResource
from talkzoho.projects.log_resource import LogResource


class ProjectsClient(ServiceClient):

    MAX_PAGE_SIZE = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def base_url(self):
        return 'https://projectsapi.zoho.{region}/restapi'.format(
            region=self.region)

    @property
    def base_query(self):
        return {'authtoken': self.auth_token}

    def __getattr__(self, attr):
        """
        Translates attribute access to Zoho Projects module names.
        e.g. . becomes Leads and custom_module_8 becomes CustomModule8
        """
        components    = attr.split('_')
        resource_name = ''.join(c.lower() for c in components)
        if resource_name in ['portals']:
            return BaseResource(service=self, name=resource_name)
        elif resource_name in ['projects', 'users']:
            return PortalResource(service=self, name=resource_name)
        elif resource_name in ['forums', 'events', 'milestones', 'tasklists', 'tasks', 'bugs']:  # noqa
            return ProjectResource(service=self, name=resource_name)
        elif resource_name in ['logs']:
            return LogResource(service=self, name=resource_name)
        else:
            raise AttributeError('Unsupported resource: ' + attr)
