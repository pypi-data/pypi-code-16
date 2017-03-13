import json
import cherrypy

from cherrypy import _cpwsgi_server, _cpserver

from py_build_server.lib.http_server_skeleton import HTTPServerSkeleton
from py_build_server.lib.logger import Logger


class Api(object):
    class UpdateRequest(object):
        def __init__(self, in_dict):
            self.event = 'update'
            self.repository = in_dict.get('repository')
            self.latest_tag = in_dict.get('latest_tag')

    class Root(object):
        def __init__(self, api):
            self.api = api  # type: Api

        def decode_request(self, in_dict):
            event = in_dict.get('event')
            if event == 'update':
                request = Api.UpdateRequest(in_dict)
                repo = self.api.repositories.get(request.repository)
                if repo is None:
                    self.api.logger.info('specified repository ({}) is not registered'
                                         .format(request.repository))
                else:
                    repo.queue.put(json.dumps(dict(event=event, latest=request.latest_tag)))

        @cherrypy.expose(alias='/api')
        @cherrypy.tools.json_in()
        def index(self):
            if self.api.strict_port_checking:  # TODO: this seems rather a hacky method of
                                               # TODO: isolating the API
                                               # TODO: look into alternative methods later
                port = str(cherrypy.request.headers.get('host').split(':')[-1])
                if port != str(self.api.cherrypy_server.bind_addr[1]):
                    self.api.logger.debug('requested port: {}. configured port: {}'
                                          .format(port, self.api.cherrypy_server.bind_addr[1]))
                    return
            self.decode_request(cherrypy.request.json)

    def __init__(self):
        self.repositories = {}
        self.strict_port_checking = False
        self.adapter = None  # type: _cpserver.ServerAdapter
        self.logger = Logger('api')
        self.cherrypy_server = _cpwsgi_server.CPWSGIServer()

    def register_new_repo(self, repo):
        self.repositories[repo.name] = repo

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
