import cherrypy
from cherrypy.process import plugins
import schedule
import threading
import time


class Plugin(plugins.SimplePlugin):
    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)
        self.schedule = schedule.Scheduler()
        self.is_running = True
        self.thread = threading.Thread(target=self.start_polling)
        self.thread.start()

    def start_polling(self):
        while self.is_running:
            self.schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.is_running = True
        self.bus.subscribe("get-schedule", self.get_schedule)

    def stop(self):
        self.is_running = False
        self.bus.unsubscribe("get-schedule", self.get_schedule)

    def get_schedule(self):
        return self.schedule


class Tool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.set_telegram_tool,
                               priority=20)

    @staticmethod
    def set_telegram_tool():
        cherrypy.request.schedule = cherrypy.engine.publish('get-schedule').pop()
