import json
from project import Project

class Story(object):
    def __init__(self, pivotal):
        self.pivotal = pivotal
        self.stories_url = pivotal.base_url + 'projects/%s/stories/'

    # Get stories matching the query in @params
    def get_all(self, project_id, params=None):
        url = self.stories_url % (str(project_id))
        r = self.pivotal.make_api_request(url, 'GET', params=params)
        return r.json()

    # Create new story with @data
    def create(self, project_id, data):
        url = self.stories_url % (str(project_id))
        r = self.pivotal.make_api_request(url, 'POST', data=data)
        return r.json()

    # Get story specified by @story_id
    def get(self, project_id, story_id):
        url = self.stories_url % (str(project_id)) + story_id + '/'
        r = self.pivotal.make_api_request(url, 'GET')
        return r.json()

    # Update story specified by @story_id
    def update(self, project_id, story_id, data):
        url = self.stories_url % (str(project_id)) + story_id + '/'
        r = self.pivotal.make_api_request(url, 'PUT', data=data)
        return r.json()

    # Post comment on story specified by @story_id
    def post_comment(self, project_id, story_id, data):
        url = self.stories_url % (str(project_id)) + story_id + '/comments/'
        r = self.pivotal.make_api_request(url, 'POST', data=data)
        return r.json()
