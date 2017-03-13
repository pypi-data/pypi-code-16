import json
import time
import cherrypy

from cherrypy import _cpwsgi_server, _cpserver
from multiprocessing import Process

from py_build_server.lib.http_server_skeleton import HTTPServerSkeleton
from py_build_server.lib.logger import Logger


def get_updater(config):
    if config.update_method.method == 'polling':
        return PollingUpdater()
    if config.update_method.method == 'github_webhook':
        return GithubWebhookUpdater()


class Updater(object):
    def __init__(self):
        self.repositories = {}
        self.logger = Logger('updater')

    def register_new_repo(self, repo):
        self.repositories[repo.name] = repo

    def start(self):
        raise NotImplementedError

    def check_repo(self, repo):
        raise NotImplementedError

    def load_config(self, config):
        pass


class GithubWebhookUpdater(Updater):
    class WebhookResponse(object):
        def __init__(self, in_dict):
            self.ref = in_dict.get('ref')
            self.tag = self.ref.split('/')[-1]
            self.is_tagged_push = 'tags' in self.ref
            self.repository = in_dict.get('repository').get('name')

    class Root(object):
        def __init__(self, updater):
            self.updater = updater

        @cherrypy.expose(alias='/github')
        @cherrypy.tools.json_in()
        def index(self):
            # openscan requests make the logs messy, this block drops anything
            # that cant be decoded to JSON
            try:
                request = GithubWebhookUpdater.WebhookResponse(cherrypy.request.json)
                if request.is_tagged_push:
                    repo = self.updater.repositories.get(request.repository)
                    repo.latest_tag = request.tag
                    repo.queue.put(json.dumps(dict(event='new_tag', latest=request.tag)))
            except AttributeError:
                pass
            return 'woot'

    def __init__(self):
        super(GithubWebhookUpdater, self).__init__()
        self.cherrypy_server = _cpwsgi_server.CPWSGIServer()
        self.adapter = None  # type: _cpserver.ServerAdapter

    def start(self):
        HTTPServerSkeleton.start()

    def load_config(self, config):
        self.cherrypy_server.bind_addr = (config.update_method.listen_address,
                                          config.update_method.port)
        cherrypy.tree.mount(self.Root(self), config.update_method.subdomain)
        self.adapter = _cpserver.ServerAdapter(cherrypy.engine,
                                               self.cherrypy_server,
                                               self.cherrypy_server.bind_addr)
        self.adapter.subscribe()


class PollingUpdater(Updater):
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
