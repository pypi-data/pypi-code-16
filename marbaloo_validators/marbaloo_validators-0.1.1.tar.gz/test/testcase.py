import cherrypy
import marbaloo_validators
from cherrypy.test import helper


class CPTest(helper.CPWebCase):

    def setup_server():
        marbaloo_validators.Plugin(cherrypy.engine).subscribe()
        cherrypy.tools.validators = marbaloo_validators.Tool()

        class Root(object):
            @cherrypy.expose
            def set_value(self, test_val):
                validators = cherrypy.request.validators
                if validators.email(test_val):
                    return 'TRUE'
                else:
                    return 'FALSE'

        cherrypy.tree.mount(Root(), '/', {
            '/': {
                'tools.validators.on': True
            }
        })
    setup_server = staticmethod(setup_server)

    def test_simple_ok(self):
        import urllib.parse
        self.getPage("/set_value", method='POST', body=urllib.parse.urlencode({'test_val': 'example@site.com'}))
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'text/html;charset=utf-8')
        self.assertBody('TRUE')

    def test_simple_fail(self):
        import urllib.parse
        self.getPage("/set_value", method='POST', body=urllib.parse.urlencode({'test_val': 'exampl@e'}))
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'text/html;charset=utf-8')
        self.assertBody('FALSE')
