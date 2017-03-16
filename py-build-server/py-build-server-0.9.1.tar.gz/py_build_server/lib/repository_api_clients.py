import json

from requests import Session


def get_client(repo):
    if repo.config.repository_api.type == 'github':
        return GithubApiClient(repo)
    if repo.config.repository_api.type == 'bitbucket':
        return BitbucketApiClient(repo)


class ApiClient(object):
    def __init__(self, repo):
        self.repo = repo  # type: ExtendedRepo
        self.type = repo.config.repository_api.type
        self.owner = repo.config.repository_api.owner
        self.target_url = repo.config.repository_api.target_url
        self._session = Session()
        self._session.auth = (repo.config.repository_api.username,
                              repo.config.repository_api.password)


class GithubApiClient(ApiClient):
    pending = 'pending'
    success = 'success'
    error = 'error'
    failure = 'failure'

    def __init__(self, repo):
        super(GithubApiClient, self).__init__(repo)
        self.context = repo.config.repository_api.context
        self.url = (
            'https://api.github.com/repos/{owner}/{repo_name}/statuses/%s'
            .format(owner=self.owner, repo_name=self.repo.name))

    def update_build_status(self, state, ref):
        self._session.post(self.url % ref,
                           data=json.dumps(
                               dict(state=state,
                                    target_url=self.target_url,
                                    description="Current status of build",
                                    context=self.context)))


class BitbucketApiClient(ApiClient):
    pending = 'INPROGRESS'
    success = 'SUCCESSFUL'
    error = 'FAILED'
    failure = 'FAILED'

    def __init__(self, repo):
        super(BitbucketApiClient, self).__init__(repo)
        self.key = repo.config.repository_api.key
        self.name = repo.config.repository_api.name
        self.url = (
            'https://api.bitbucket.org/2.0/repositories/{owner}/{repo_name}/commit/%s/statuses/build'
            .format(owner=self.owner, repo_name=self.repo.name))

    def update_build_status(self, state, ref):
        self._session.post(self.url % ref,
                           data=dict(state=state, key=self.key,
                                     url=self.target_url,
                                     description="Current status of build"))
