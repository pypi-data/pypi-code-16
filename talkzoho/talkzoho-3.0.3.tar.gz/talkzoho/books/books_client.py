from talkzoho.service_client import ServiceClient
from talkzoho.books.base_resource import BaseResource


class BooksClient(ServiceClient):

    SCOPE = 'booksapi'
    MAX_PAGE_SIZE = 200

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def base_url(self):
        return 'https://books.zoho.{region}/api/v3'.format(
            region=self.region)

    @property
    def base_query(self):
        return {
            'scope': self.SCOPE,
            'authtoken': self.auth_token}

    def __getattr__(self, attr):
        """
        Translates attribute access to Zoho Projects module names.
        e.g. .price_books becomes pricebooks.
        """
        components    = attr.split('_')
        resource_name = ''.join(c.lower() for c in components)
        return BaseResource(service=self, name=resource_name)
