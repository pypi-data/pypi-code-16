import requests
import pprint
import json


class FlexioPipe:
    def __init__(self, connection=None, identifier=None, data=None):
        self.connection = connection
        self.data = data
        if data:
            self.eid = data['eid']
            self.identifier = data['eid']
        elif identifier:
            self.identifier = identifier
        assert connection

    @property
    def ename(self):
        return self.data['ename']

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    def run(self, params={}, files={}, output=None):
        url = 'https://{0}/api/v1/pipes/{1}/run'.format(self.connection.host,self.identifier)
        if output:
            url += '?stream=0'
        headers = {'Authorization': "Bearer %s" % self.connection.api_key}
        stream = True if output else False
        response = requests.post(url, data=params, files=files, verify=False, headers=headers, stream=stream)
        if stream:
            for chunk in response.iter_content(4096):
                output.write(chunk)

class Flexio:
    def __init__(self, api_key = None, host = "www.flex.io"):
        self.api_key = api_key
        self.host = host

    def pipes(self):
        response = requests.get("https://%s/api/v1/pipes" % self.host, verify=False, headers={'Authorization': "Bearer %s" % self.api_key})
        collection = json.loads(response.text)
        ret = []
        for obj in collection:
            pipe = FlexioPipe(connection=self, data=obj)
            ret.append(pipe)
        return ret

    def pipe(self, identifier):
        return FlexioPipe(connection=self, identifier=identifier)

    def run():
        return True

