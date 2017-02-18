import cherrypy
import marbaloo_dogpile
from cherrypy.test import helper
import os


class CPTest(helper.CPWebCase):

    def setup_server():
        marbaloo_dogpile.Plugin(cherrypy.engine).subscribe()
        cherrypy.tools.dogpile = marbaloo_dogpile.Tool()

        class Root(object):
            @cherrypy.expose
            def set_value(self, test_val):
                dogpile = cherrypy.request.dogpile
                dogpile.set('test_val', test_val)
                return dogpile.get('test_val')

        root_path = os.path.dirname(__file__)
        dogpile_dbm_path = os.path.join(root_path, 'dogpile.dbm')

        cherrypy.config['marbaloo_dogpile'] = {
            'backend': 'dogpile.cache.dbm',
            'expiration_time': 3600,
            'arguments': {'filename': dogpile_dbm_path},
        }
        cherrypy.tree.mount(Root(), '/', {
            '/': {
                'tools.dogpile.on': True
            }
        })
    setup_server = staticmethod(setup_server)

    def test_simple(self):
        import urllib.parse
        self.getPage("/set_value", method='POST', body=urllib.parse.urlencode({'test_val': '123456'}))
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'text/html;charset=utf-8')
        self.assertBody('123456')
