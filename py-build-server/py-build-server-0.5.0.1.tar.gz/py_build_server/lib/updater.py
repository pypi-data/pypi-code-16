import json
import time
import cherrypy

from cherrypy import _cpwsgi_server, _cpserver
from multiprocessing import Process

from py_build_server.lib.http_server_skeleton import HTTPServerSkeleton
from py_build_server.lib.logger import Logger
from py_build_server.lib.repository_hooks import RepositoryListener


def get_updaters(config):
    updaters = []
    for method in config.update_method.methods:
        if method == 'polling':
            updaters.append(PollingUpdater())
        if method == 'github_webhook':
            updaters.append(GithubWebhookUpdater())
        if method == 'bitbucket_webhook':
            updaters.append(BitbucketWebhookUpdater())
    return updaters


class Updater(RepositoryListener):
    update_method = 'update'

    def __init__(self):
        super(Updater, self).__init__()
        self.logger = Logger('updater')

    def check_repo(self, repo):
        pass

    def register_new_repo(self, repo):
        if repo.config.update_method == self.update_method:
            super(Updater, self).register_new_repo(repo)

    def start(self):
        raise NotImplementedError


class WebhookUpdater(Updater):
    update_method = 'webhook'

    def start(self):
        HTTPServerSkeleton.start()

    class WebhookRequest(object):
        def __init__(self, in_dict):
            self.ref = self.ref or ''
            self.tag = self.ref.split('/')[-1]
            self.is_tagged_push = 'tags' in self.ref
            self.repository = in_dict.get('repository').get('name')

    class Root(object):
        def __init__(self, updater):
            self.updater = updater

        def index(self, request):
                if request.is_tagged_push and request.created:
                    repo = self.updater.repositories.get(request.repository)
                    repo.latest_tag = request.tag
                    repo.queue.put(json.dumps(dict(event='new_tag', latest=request.tag)))

    def __init__(self):
        super(WebhookUpdater, self).__init__()
        self.cherrypy_server = _cpwsgi_server.CPWSGIServer()
        self.adapter = None  # type: _cpserver.ServerAdapter

    def load_config(self, config):
        self.cherrypy_server.bind_addr = (config.listen_address,
                                          config.port)
        cherrypy.tree.mount(self.Root(self), config.subdomain)
        self.adapter = _cpserver.ServerAdapter(cherrypy.engine,
                                               self.cherrypy_server,
                                               self.cherrypy_server.bind_addr)
        self.adapter.subscribe()


class BitbucketWebhookUpdater(WebhookUpdater):
    update_method = 'bitbucket_webhook'

    class BitbucketWebhookRequest(WebhookUpdater.WebhookRequest):
        def __init__(self, in_dict):
            ref_changes = in_dict.get('refChanges', {})
            self.ref = ref_changes.get('refId')
            self.created = ref_changes.get('type') == 'UPDATE'
            super(BitbucketWebhookUpdater.BitbucketWebhookRequest, self).__init__(in_dict)

    class Root(WebhookUpdater.Root):
        @cherrypy.expose(alias='/bitbucket')
        @cherrypy.tools.json_in()
        def index(self, *args):
            try:
                request = BitbucketWebhookUpdater.BitbucketWebhookRequest(cherrypy.request.json)
                super(BitbucketWebhookUpdater.Root, self).index(request)
            except AttributeError:
                pass
            return

    def load_config(self, config):
        conf = config.update_method.methods.get(self.update_method)
        super(BitbucketWebhookUpdater, self).load_config(conf)


class GithubWebhookUpdater(WebhookUpdater):
    update_method = 'github_webhook'

    class GithubWebhookRequest(WebhookUpdater.WebhookRequest):
        def __init__(self, in_dict):
            self.ref = in_dict.get('ref')
            self.created = in_dict.get('created')
            super(GithubWebhookUpdater.GithubWebhookRequest, self).__init__(self.ref)

    class Root(WebhookUpdater.Root):
        @cherrypy.expose(alias='/github')
        @cherrypy.tools.json_in()
        def index(self, *args):
            try:
                request = GithubWebhookUpdater.GithubWebhookRequest(cherrypy.request.json)
                super(GithubWebhookUpdater.Root, self).index(request)
            except AttributeError:
                pass
            return

    def load_config(self, config):
        conf = config.update_method.methods.get(self.update_method)
        super(GithubWebhookUpdater, self).load_config(conf)


class PollingUpdater(Updater):
    update_method = 'polling'

    def __init__(self):
        super(PollingUpdater, self).__init__()
        self.processes = []

    def start(self):
        for repo in self.repositories.values():
            repo.logger.debug('creating PollingUpdater process for {}'.format(repo.name))
            p = Process(target=self.check_repo, args=(repo, ))
            p.start()
            self.processes.append(p)

        self.logger.debug('Finished creating processes for PollingUpdater')
        for p in self.processes:
            p.join()

    def check_repo(self, repo):
        while True:
            self.logger.info('Checking status of {}'.format(repo.name))
            if repo.config.branch is not None:
                if repo.config.branch != str(repo.active_branch):
                    raise Exception(msg='repository is not on the correct branch({} != {})'
                                    .format(repo.active_branch, repo.config.branch))

            status = repo.get_status()
            latest_tag = [tag for tag in reversed(sorted(
                str(tag) for tag in repo.tags
            )) if tag != 'origin'][0]
            if status.behind:
                repo.queue.put(json.dumps(dict(event='new_tag', latest=latest_tag)))
            self.logger.debug('waiting {} minutes'.format(repo.config.fetch_frequency))
            try:
                time.sleep(repo.config.fetch_frequency * 60)
            except KeyboardInterrupt:
                self.logger.debug('exited while waiting to check repo again')
                return
