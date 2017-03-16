import cherrypy

from py_build_server.lib.logger import Logger


class HTTPServerSkeleton(object):
    is_running = False
    logger = Logger('cherrypy')

    @staticmethod
    def start():
        if HTTPServerSkeleton.is_running:
            return
        # hackery to stop cherrypy outputting log to stdout (spams journald when ran
        # in the foreground as a systemd service. all logs from cherrypy will now be
        # routed to syslog instead (journal if running systemd)
        cherrypy.log.screen = False
        cherrypy.log.error_log.log = HTTPServerSkeleton.logger.log
        cherrypy.log.error_log.propagate = False
        cherrypy._cpchecker.Checker.on = False  # stops cherrypy checking for config
        cherrypy.engine.signals.subscribe()
        cherrypy.engine.start()
        cherrypy.log.access_log.log = HTTPServerSkeleton.logger.log
        cherrypy.log.access_log.propagate = False
        HTTPServerSkeleton.is_running = True

    @staticmethod
    def stop():
        if HTTPServerSkeleton.is_running:
            cherrypy.engine.exit()
            HTTPServerSkeleton.is_running = False

