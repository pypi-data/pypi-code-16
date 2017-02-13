import requests


class Service(object):
    def __init__(self, host):
        self.host = host

    def C(self, res, doc):
        ret = requests.post(self.host+res, json=doc)
        ret.raise_for_status()
        return ret.json()

    def Q(self, res, qry):
        ret = requests.get(self.host+res, params=qry, json=[])
        ret.raise_for_status()
        return ret.json()

    def R(self, res):
        ret = requests.get(self.host+res, json=[])
        ret.raise_for_status()
        return ret.json()

    def U(self, res, doc):
        ret = requests.put(self.host+res, json=doc)
        ret.raise_for_status()
        return ret.json()

    def D(self, res):
        ret = requests.delete(self.host+res)
        ret.raise_for_status()
        return ret.json()
