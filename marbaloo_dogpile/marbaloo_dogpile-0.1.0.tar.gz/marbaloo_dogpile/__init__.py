import cherrypy
from cherrypy.process import plugins
from dogpile.cache import make_region


class Plugin(plugins.SimplePlugin):
    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)
        self.region = None

    def start(self):
        if cherrypy.config.get('marbaloo_dogpile') is not None:
            self.region = make_region().configure(**cherrypy.config.get('marbaloo_dogpile'))
            self.bus.subscribe('get-dogpile', self.get_dogpile)
        else:
            print('dogpile configuration is not set.')
            raise Exception

    def stop(self):
        self.bus.unsubscribe('get-dogpile', self.get_dogpile)

    def get_dogpile(self):
        return self.region


class Tool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.set_dogpile_tool,
                               priority=20)

    def _setup(self):
        cherrypy.Tool._setup(self)

    @staticmethod
    def set_dogpile_tool():
        cherrypy.request.dogpile = cherrypy.engine.publish('get-dogpile').pop()
