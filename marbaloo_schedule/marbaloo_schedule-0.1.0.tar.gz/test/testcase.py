import cherrypy
from cherrypy.test import helper


class CPTest(helper.CPWebCase):

    def setup_server():
        import marbaloo_schedule
        import time

        marbaloo_schedule.Plugin(cherrypy.engine).subscribe()
        cherrypy.tools.schedule = marbaloo_schedule.Tool()

        class Root(object):
            job_completed = False

            def do_schedule_jobs(self):
                self.job_completed = True

            @cherrypy.expose
            def index(self):
                schedule = cherrypy.request.schedule
                schedule.every(2).seconds.do(self.do_schedule_jobs)

                def content():
                    while True:
                        if self.job_completed:
                            yield 'success'
                            break
                        else:
                            time.sleep(1)
                return content()
            index._cp_config = {'response.stream': True}

        cherrypy.tree.mount(Root(), '/', {
                                '/': {
                                    'tools.schedule.on': True
                                }
                            })
    setup_server = staticmethod(setup_server)

    def test_simple(self):
        self.getPage("/")
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'text/html;charset=utf-8')
        self.assertBody('success')
