class Project(object):
    def __init__(self, pivotal):
        self.pivotal = pivotal
        self.project_url = pivotal.base_url + 'projects/%s/'

    # Get a project specified by @project_id
    def get(self, project_id):
        url = self.project_url % (str(project_id))
        r = self.pivotal.make_api_request(url, 'GET')
        return r.json()

    # Get memberships of a project specified by @project_id
    def get_memberships(self, project_id):
        url = self.project_url % (str(project_id)) + 'memberships/'
        r = self.pivotal.make_api_request(url, 'GET')
        return r.json()
