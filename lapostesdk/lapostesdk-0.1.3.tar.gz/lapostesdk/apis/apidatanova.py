from lapostesdk.apis.apibase import ApiBase

class ApiDatanova(ApiBase):
    def __init__(self, api_key):
        super(ApiDatanova, self).__init__(api_key, product='datanova')

    def pointscontact(self, q):
        payload = {'q': q}
        #return self.get('pointscontact', params=payload)

        return self.create_object(self._get('pointscontact', params=payload), 'Xxx')

    def codespostaux(self, q):
        payload = {'q': q}
        return self.get('codespostaux', params=payload)

    def servicesbureaux(self, q):
        payload = {'q': q}
        return self.get('servicesbureaux', params=payload)

    def boitesrue(self, q):
        payload = {'q': q}
        return self.get('boitesrue', params=payload)

    def communesnouvelles(self, q):
        payload = {'q': q}
        return self.get('communesnouvelles', params=payload)

    def horairesbureaux(self, q):
        payload = {'q': q}
        return self.get('horairesbureaux', params=payload)

    def automatesbureaux(self, q):
        payload = {'q': q}
        return self.get('automatesbureaux', params=payload)

    def accessibilitebureaux(self, q):
        payload = {'q': q}
        return self.get('accessibilitebureaux', params=payload)
