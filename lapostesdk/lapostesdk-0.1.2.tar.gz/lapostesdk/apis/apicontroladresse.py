from lapostesdk.apis.apibase import ApiBase

class ApiControlAdresse(ApiBase):
    def __init__(self, api_key):
        super(ApiControlAdresse, self).__init__(api_key,
                product='controladresse', entity='Adresse')

    def search(self, address):
        payload = {'q': address}
        return self._get('adresses', params=payload)

