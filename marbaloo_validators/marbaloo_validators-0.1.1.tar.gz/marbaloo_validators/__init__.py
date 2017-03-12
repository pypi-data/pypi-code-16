import cherrypy
from cherrypy.process import plugins
import validators


class Plugin(plugins.SimplePlugin):
    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)
        self.validators = validators

    def start(self):
        self.bus.subscribe('get-validators', self.get_validators)

    def stop(self):
        self.bus.unsubscribe('get-validators', self.get_validators)

    def get_validators(self):
        return self.validators


class Tool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.set_tool,
                               priority=20)

    def _setup(self):
        cherrypy.Tool._setup(self)

    @staticmethod
    def set_tool():
        cherrypy.request.validators = cherrypy.engine.publish('get-validators').pop()
