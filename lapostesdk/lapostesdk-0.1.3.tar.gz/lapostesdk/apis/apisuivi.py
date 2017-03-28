from lapostesdk.apis.apibase import ApiBase

class ApiSuivi(ApiBase):
    def __init__(self, api_key):
        super(ApiSuivi, self).__init__(api_key, product='suivi', entity='Suivi')

    def get(self, resource, params={}):
        response = self._get(resource, params)

        if response['code'] == 'BAD_REQUEST':
            raise Exception(response['message'])

        if response['code'] == 'RESOURCE_NOT_FOUND':
            raise Exception(response['message'])

        if self.entity is None:
            return response

        return self.create_object(response, self.entity)
