import cherrypy
from .recaptcha import ReCaptcha


class Tool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.set_tool,
                               priority=20)

    def _setup(self):
        cherrypy.Tool._setup(self)

    @staticmethod
    def set_tool(secret_key='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
                 site_key='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
                 remoteip=''):  # Default Keys for development, do not use for production.
        cherrypy.request.recaptcha = ReCaptcha()
        cherrypy.request.recaptcha.secret_key = secret_key
        cherrypy.request.recaptcha.site_key = site_key
        cherrypy.request.recaptcha.remoteip = remoteip

        inner_verify = cherrypy.request.recaptcha.verify

        def verify():
            return inner_verify(cherrypy.request.params.get('g-recaptcha-response'))

        cherrypy.request.recaptcha.verify = verify
