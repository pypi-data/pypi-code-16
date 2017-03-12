from werkzeug.routing import Rule
import ioc

from wizards.wsgi.ctrl import NotImplementedCtrl


class Endpoint:
    """Represents a WSGI endpoint."""
    response_class = ioc.class_property('WSGIResponse')
    codec = ioc.class_property('WSGIRequestSerializer')
    authenticator = ioc.class_property('WSGIRequestAuthenticator')

    @property
    def content_types(self):
        """Return a set of content types specifying in which
        formats the endpoint is able to respond.
        """
        return self.codec.content_types

    @property
    def accepts(self):
        """Return a set of content types specifying in which
        formats the endpoint is able to accept requests.
        """
        return self.codec.content_types

    def __init__(self, name, url, aud=None, roles=None, authenticate=True,
        authorizations=None, methods=None, content_types=None, **kwargs):
        """Represents a WSGI endpoint.

        Args:
            name: a string specifying the name of the endpoint.
            url: the URL.
            requires_authentication: a boolean indicating if
                only authenticated requests may request this
                resource. Default is ``True``.
            aud: endpoint will accept requests targeted at this
                audience (list of strings).
            roles: authenticated subject must have at least one
                of these roles (list of strings).
            authorizations: authenticated subject must have all
                of the authorizations (list of strings).
            methods: either a list of strings of a dictionary
                further specifying options for each request
                method.
        """
        self.rule = Rule(url, endpoint=name, methods=methods)
        self.name = name
        self.url = url
        self.ctrl = ioc.require("%s:ctrl" % name,
            default=NotImplementedCtrl.as_view())
        self.aud = set(aud or [])
        self.roles = set(roles or [])
        self.authenticate = authenticate
        self.authorizations = authorizations
        self.empty = False
        self.methods = methods or set([])

    def validate(self, request):
        return

    def authorize(self, request):
        """Authorize `request`."""
        code = None
        hint = None
        message= None
        if self.authenticate and not request.is_authenticated():
            request.reject('AUTHENTICATION_REQUIRED')

        subject = request.subject
        if self.aud and subject.aud not in self.aud:
            code = 'SUBJECT_NOT_AUTHORIZED'
            message = "'%s' is not an audience of this endpoint" % request.aud
            hint = "The request specified an invalid audience "\
                "for this endpoint: %s" % request.aud

        if self.roles and not (self.roles & subject.roles):
            code = 'SUBJECT_NOT_AUTHORIZED'

        if self.authorizations and\
        not subject.has_authorizations(self.authorizations):
            code = 'SUBJECT_NOT_AUTHORIZED'

        if code is not None:
            request.reject(code, message=message, hint=hint)

    def handle(self, request):
        self.authorize(request)
        return self.ctrl(request)
