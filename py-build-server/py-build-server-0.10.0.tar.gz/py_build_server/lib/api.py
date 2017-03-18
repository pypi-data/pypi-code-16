import json
import cherrypy

from cherrypy import _cpwsgi_server, _cpserver

from py_build_server.lib.http_server_skeleton import HTTPServerSkeleton
from py_build_server.lib.logger import Logger
from py_build_server.lib.repository_hooks import RepositoryListener


class Api(RepositoryListener):
    class UpdateRequest(object):
        def __init__(self, in_dict):
            self.event = 'update'
            self.repository = in_dict.get('repository')
            self.latest_tag = in_dict.get('latest_tag')

    class GenericRequest(object):
        def __init__(self, in_dict):
            self.repository = None
            self.event = None
            if self._sanity_check(in_dict):
                self.__dict__.update(in_dict)

        def _sanity_check(self, in_dict):
            for key in in_dict:
                if key not in self.__dict__:
                    return False
            return True

    class Root(object):
        def __init__(self, api):
            self.api = api  # type: Api

        def decode_request(self, in_dict):
            event = in_dict.get('event')
            if event == 'new_tag':
                request = Api.UpdateRequest(in_dict)
                repo = self.api.repositories.get(request.repository)
                if repo is None:
                    self.api.logger.info('specified repository ({}) is not registered'
                                         .format(request.repository))
                    return dict(status='failure', reason='repository not found')
                else:
                    repo.queue.put(json.dumps(dict(event=event, latest=request.latest_tag)))
                    return dict(status='success')
            if event == 'list_repositories':
                return dict(repositories=[repo for repo in self.api.repositories])
            if event == 'list_repository':
                request = Api.GenericRequest(in_dict)
                repo = self.api.repositories.get(request.repository)
                return dict(repository=repo.to_dict())

        @cherrypy.expose()
        @cherrypy.tools.json_in()
        @cherrypy.tools.json_out()
        def index(self):
            if self.api.strict_port_checking:  # TODO: this seems rather a hacky method of
                                               # TODO: isolating the API
                                               # TODO: look into alternative methods later
                port = str(cherrypy.request.headers.get('host').split(':')[-1])
                if port != str(self.api.cherrypy_server.bind_addr[1]):
                    self.api.logger.debug('requested port: {}. configured port: {}'
                                          .format(port, self.api.cherrypy_server.bind_addr[1]))
                    return
            return self.decode_request(cherrypy.request.json)

    def __init__(self):
        super(Api, self).__init__()
        self.strict_port_checking = False
        self.adapter = None  # type: _cpserver.ServerAdapter
        self.logger = Logger('api')
        self.cherrypy_server = _cpwsgi_server.CPWSGIServer()

    def load_config(self, config):
        self.strict_port_checking = config.api.strict_port_checking
        self.cherrypy_server.bind_addr = (config.api.listen_address,
                                          config.api.port)
        cherrypy.tree.mount(self.Root(self), config.api.subdomain)
        self.adapter = _cpserver.ServerAdapter(cherrypy.engine,
                                               self.cherrypy_server,
                                               self.cherrypy_server.bind_addr)
        self.adapter.subscribe()

    def start(self):
        HTTPServerSkeleton.start()
