import cherrypy


class HTTPServerSkeleton(object):
    is_running = False

    @staticmethod
    def start():
        if HTTPServerSkeleton.is_running:
            return
        cherrypy.config.update({'log.screen': False,
                                'log.access_file': '',
                                'log.error_file': ''})
        cherrypy.engine.signals.subscribe()
        cherrypy.engine.start()
        HTTPServerSkeleton.is_running = True

    @staticmethod
    def stop():
        if HTTPServerSkeleton.is_running:
            cherrypy.engine.exit()
            HTTPServerSkeleton.is_running = False
