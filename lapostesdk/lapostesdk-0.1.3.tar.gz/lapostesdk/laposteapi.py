from lapostesdk.apis import apisuivi, apicontroladresse

class LaPosteApi(object):
    def __init__(self, api_key):
        self.api_key = api_key

        self.suivi = apisuivi.ApiSuivi(self.api_key)
        self.controladresse = apicontroladresse.ApiControlAdresse(self.api_key)
