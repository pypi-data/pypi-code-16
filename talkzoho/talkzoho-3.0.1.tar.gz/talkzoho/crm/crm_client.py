from urllib.parse import urlencode
from collections import namedtuple

from tornado.escape import json_decode

from talkzoho.service_client import ServiceClient
from talkzoho.crm.crm_resource import CRMResource
from talkzoho import logger


ModuleMap = namedtuple('ModuleMap', 'canonical_name, singular_alias, plural_alias')  # noqa


class CRMClient(ServiceClient):

    SCOPE              = 'crmapi'
    MAX_PAGE_SIZE      = 200

    def __init__(self, *args, use_module_aliases=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_module_aliases = use_module_aliases

    @property
    def base_url(self):
        return 'https://crm.zoho.{region}/crm/private/json'.format(
            region=self.region)

    @property
    def base_query(self):
        return {
            'scope': self.SCOPE,
            'authtoken': self.auth_token}

    async def get_module_maps(self):
        # TODO: only do if map alias is True
        url  = '{base_url}/Info/getModules?{query}'.format(
            base_url=self.base_url,
            query=urlencode(self.base_query))

        logger.info('GET: {}'.format(url))
        response = await self.http_client.fetch(url)

        body = json_decode(response.body.decode('utf-8'))
        maps = body['response']['result']['row']

        return [ModuleMap(
            canonical_name=m['content'],
            singular_alias=m['sl'],
            plural_alias=m['pl']) for m in maps]

    def __getattr__(self, attr):
        """
        Translates attribute access to Zoho CRM module names.
        e.g. leads becomes Leads and custom_module_8 becomes CustomModule8
        """
        components  = attr.split('_')
        module_name = ''.join(c.title() for c in components)
        return CRMResource(service=self, name=module_name)
