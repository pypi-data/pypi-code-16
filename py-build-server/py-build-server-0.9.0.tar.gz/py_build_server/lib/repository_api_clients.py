from github3 import login
from pybitbucket.auth import BasicAuthenticator
from pybitbucket.bitbucket import Client

from py_build_server.lib.repo_extentions import ExtendedRepo


def get_client(repo):
    if repo.config.repository_api.type == 'github':
        return GithubApiClient(repo)
    if repo.config.repository_api.type == 'bitbucket':
        return BitbucketApiClient(repo)


class ApiClient(object):
    pending = 'pending'
    success = 'success'
    error = 'error'
    failure = 'failure'

    def __init__(self, repo):
        self.repo = repo  # type: ExtendedRepo
        self.type = repo.config.repository_api.type
        self.owner = repo.config.repository_api.owner
        self.target_url = repo.config.repository_api.target_url


class GithubApiClient(ApiClient):
    def __init__(self, repo):
        super(GithubApiClient, self).__init__(repo)
        self.github = login(repo.config.repository_api.username,
                            repo.config.repository_api.password)
        self.context = repo.config.repository_api.context
        self.user = self.github.user()
        self.url = ('https://api.github.com/repos/{owner}/{repo_name}/statuses/%s'
                    .format(owner=self.owner, repo_name=self.repo.name))

    def update_build_status(self, state, ref):
        self.user._post((self.url % ref),
                        data=dict(state=state,
                                  target_url=self.target_url,
                                  description="Current status of build",
                                  context=self.context))


class BitbucketApiClient(ApiClient):
    status_map = dict(pending='INPROGRESS',
                      success='SUCCESSFUL',
                      error='FAILED',
                      failure='FAILED')

    def __init__(self, repo):
        super(BitbucketApiClient, self).__init__(repo)
        self.key = repo.config.repository_api.context
        self.name = repo.config.repository_api.name
        self.email = repo.config.repository_api.email
        self.client = Client(BasicAuthenticator(repo.config.repository_api.username,
                                                repo.config.repository_api.password,
                                                repo.config.repository_api.email))
        self.url = ('https://api.bitbucket.org/2.0/repositories/{owner}/{repo_name}/commit/%s/statuses/build'
                    .format(owner=self.owner, repo_name=self.repo.name))

    def update_build_status(self, state, ref):
        self.client.session.post((self.url % ref),
                                 data=dict(state=self.status_map.get(state), key=self.key,
                                           name=self.name, url=self.target_url,
                                           description="Current status of build"))
