import requests
from requests.auth import AuthBase
from project import Project
from story import Story

class PivotalAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['X-TrackerToken'] = self.token
        return r

class PivotalClient(object):
    def __init__(self, token):
        self.base_url = 'https://www.pivotaltracker.com/services/v5/'
        self.auth = PivotalAuth(token)

        self.project = Project(self)
        self.story = Story(self)

    def make_api_request(self, url, method, params=None, data=None):
        if method is 'POST' or 'PUT':
            headers = {'Content-Type' : 'application/json' }

        r = requests.request(method, url, auth=self.auth, headers=headers, params=params, data=data)
        if r.status_code != 200:
            print 'Error performing ' + method + ' to ' + url + ', got status code: ' + str(r.status_code) + '\n'
            raise IOError(r.reason)
        return r
