from talkzoho.service_client import ServiceClient
from talkzoho.support.base_resource import BaseResource


class SupportClient(ServiceClient):

    MAX_PAGE_SIZE = 200

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def base_url(self):
        return 'https://support.zoho.{region}/api/json'.format(
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
        return BaseResource(service=self, name=resource_name)
