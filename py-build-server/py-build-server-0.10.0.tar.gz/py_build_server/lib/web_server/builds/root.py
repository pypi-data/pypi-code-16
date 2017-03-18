import cherrypy
from cherrypy import _cpserver
from cherrypy import _cpwsgi_server

from py_build_server.lib.http_server_skeleton import HTTPServerSkeleton
from py_build_server.lib.logger import Logger
from py_build_server.lib.repository_hooks import RepositoryListener
from py_build_server.lib.web_server.html_objects import hyperlink, br, base_template, h3


class WebsiteBuilds(RepositoryListener):

    def __init__(self):
        super(WebsiteBuilds, self).__init__()
        self.logger = Logger('website-builds')
        self.cherrypy_server = _cpwsgi_server.CPWSGIServer()
        self.adapter = None  # type: _cpserver.ServerAdapter
        self.repository_subdomains = {}

    def start(self):
        for name, repo in self.repositories.items():
            server = self.BuildsRoot(repo)
            self.repository_subdomains[name] = server
            cherrypy.tree.mount(server, '%s/%s' % (self.config.subdomain, name))
        HTTPServerSkeleton.start()

    class BuildsRoot(object):
        def __init__(self, repo=None):
            self.repo = repo

        def list_builds(self):
            return base_template(
                title='Builds',
                body=(h3('Builds'),
                      br(hyperlink('?build={}'.format(build), build)
                         for build in self.repo.build_log_manager.list_builds())))

        def build_log_requested(self, build):
            return base_template(
                title='Build{}'.format(build),
                body=br(self.repo.build_log_manager.load_build(build)))

        @cherrypy.expose()
        def index(self, *args, **kwargs):
            print(kwargs)
            if 'build' in kwargs:
                return self.build_log_requested(kwargs.get('build'))
            else:
                return self.list_builds()

    class Root(object):
        def __init__(self, website_builds):
            self.website_builds = website_builds

        @cherrypy.expose()
        def index(self, *args, **kwargs):
            print(args)
            print(kwargs)
            return base_template(
                title='Builds',
                body=(h3('Builds'),
                      br(hyperlink(name)
                         for name in self.website_builds.repositories.keys())))

    def register_new_repo(self, repo):
        if hasattr(repo.config, 'repository_api'):
            super(WebsiteBuilds, self).register_new_repo(repo)

    def load_config(self, config):
        self.config = config.build_report_server
        self.cherrypy_server.bind_addr = (self.config.listen_address,
                                          self.config.port)
        cherrypy.tree.mount(self.Root(self), self.config.subdomain)
        self.adapter = _cpserver.ServerAdapter(cherrypy.engine,
                                               self.cherrypy_server,
                                               self.cherrypy_server.bind_addr)
        self.adapter.subscribe()
