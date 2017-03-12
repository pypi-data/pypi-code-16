import logging
import uuid

from wizards.wsgi.request import NO_SUBJECT_ID


class RequestAuthenticator:
    logger = logging.getLogger('wsgi.auth')

    def authenticate(self, request):
        raise NotImplementedError("Subclasses must override this method.")


class NullRequestAuthenticator(RequestAuthenticator):

    def authenticate(self, request):
        request.subject = Subject(
            sub=uuid.UUID(int=0))


class TestRequestAuthenticator(RequestAuthenticator):
    """A :class:`RequestAuthenticator` implementation
    that sets the ``Request.subject_id`` attribute to
    the value provided in the constructor.
    """

    def __init__(self, subject_id, roles=None, aud=None):
        self.subject_id = subject_id
        self.roles = set(roles or [])
        self.aud = aud

    def authenticate(self, request):
        request.subject = Subject(
            sub=self.subject_id,
            aud=self.aud,
            roles=self.roles)


class HeadersRequestAuthenticator(RequestAuthenticator):
    """A :class:`RequestAuthenticator` implementation that authenticates
    a request based on the present headers. These headers may be set
    by the upstream proxy or during automated test runs. When using
    in a production environment, make sure the proxy purges out any
    client provided header that matches one of those inspected
    by :class:`RequestAuthenticator`.

    Args:
        subject (string): specifies the header containing
            the subject identifier.
        roles (string): specifies the header containing the
            roles assigned to the subject. The content of
            the header is expected to be a comma-separated
            list.
        audience (string): specifies the header containing
            the audience.
    """

    def __init__(self, subject, roles, audience):
        self.subject = subject
        self.roles = roles
        self.audience = audience

    def authenticate(self, request):
        headers = request.headers
        sub = headers.get(self.subject) or NO_SUBJECT_ID

        cls = Subject
        if sub == NO_SUBJECT_ID:
            cls = AnonymousSubject

        request.subject = cls(
            sub=sub,
            aud=headers.get(self.audience))

        if headers.get(self.roles):
            roles = headers.get(self.roles)
            subject.rol = set(filter(bool, roles.split(',')))

        self.logger.debug("Authenticated request (subject: %s)"
            % str(request.subject))


class Subject:

    def __init__(self, sub=None, aud=None, rol=None):
        self.sub = sub
        self.aud = aud
        self.rol = rol

    def is_authenticated(self):
        return self.sub != NO_SUBJECT_ID


class AnonymousSubject(Subject):

    def is_authenticated(self):
        return False

    def __str__(self):
        return "<anonymous>"


ANONYMOUS = AnonymousSubject()
