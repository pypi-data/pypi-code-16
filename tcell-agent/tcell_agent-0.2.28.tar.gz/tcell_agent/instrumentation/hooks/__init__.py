import logging
import types

import tcell_agent

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.sensor_events import LoginEvent
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.utils import header_keys_from_request_env

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


# Easy test mocking
def get_logger():
    return LOGGER


def report_login_event(
        request_env,
        status,
        user_id,
        session_id,
        document_uri,
        user_agent=None,
        referrer=None,
        remote_address=None,
        header_keys=None):
    from tcell_hooks.hooks.v1.login import LOGIN_SUCCESS, LOGIN_FAILURE

    if user_agent is None:
        user_agent = request_env.get("HTTP_USER_AGENT")
    if referrer is None:
        referrer = request_env.get("HTTP_REFERER")
    if header_keys is None:
        header_keys = header_keys_from_request_env(request_env)
    if remote_address is None and request_env != {}:
        remote_address = better_ip_address(request_env)

    if status == LOGIN_SUCCESS:
        event = LoginEvent().success(
            user_id=user_id,
            user_agent=user_agent,
            referrer=referrer,
            remote_addr=remote_address,
            header_keys=header_keys,
            document_uri=document_uri,
            session_id=session_id)
        TCellAgent.send(event)
    elif status == LOGIN_FAILURE:
        event = LoginEvent().failure(
            user_id=user_id,
            user_agent=user_agent,
            referrer=referrer,
            remote_addr=remote_address,
            header_keys=header_keys,
            document_uri=document_uri,
            session_id=session_id)
        TCellAgent.send(event)
    else:
        get_logger().error("Unkown login status: {status}".format(status=status))


def _instrument():
    from tcell_hooks.hooks.v1.login import RegisterLoginEvent as LoginRegisterLoginEvent
    from tcell_hooks.hooks.v1.frameworks.django.login import RegisterLoginEvent as DjangoRegisterLoginEvent
    from tcell_hooks.hooks.v1.frameworks.flask.login import RegisterLoginEvent as FlaskRegisterLoginEvent

    old_login_send = LoginRegisterLoginEvent.send

    @classmethod
    def login_send(_,
                   status,
                   session_id,
                   user_agent,
                   referrer,
                   remote_address,
                   header_keys,
                   user_id,
                   document_uri,
                   user_valid=None):
        safe_wrap_function(
            "Sending Login Event",
            report_login_event,
            {},
            status,
            user_id,
            session_id,
            document_uri,
            user_agent=user_agent,
            referrer=referrer,
            remote_address=remote_address,
            header_keys=header_keys)

        return old_login_send(status, session_id, user_agent, referrer, remote_address, header_keys, user_id,
                              document_uri, user_valid)

    LoginRegisterLoginEvent.send = login_send

    old_django_send = DjangoRegisterLoginEvent.send

    @classmethod
    def django_send(_, status, django_request, user_id, session_id, user_valid=None):
        safe_wrap_function(
            "Sending Login Event",
            report_login_event,
            django_request.META,
            status,
            user_id,
            session_id,
            django_request.get_full_path())
        return old_django_send(status, django_request, user_id, session_id, user_valid)

    DjangoRegisterLoginEvent.send = django_send

    old_flask_send = FlaskRegisterLoginEvent.send

    @classmethod
    def flask_send(_, status, flask_request, user_id, session_id, user_valid=None):
        safe_wrap_function(
            "Sending Login Event",
            report_login_event,
            flask_request.environ,
            status,
            user_id,
            session_id,
            flask_request.url)
        return old_flask_send(status, flask_request, user_id, session_id, user_valid)

    FlaskRegisterLoginEvent.send = flask_send


try:
    import tcell_hooks

    if TCellAgent.get_agent():
        _instrument()
except ImportError as ie:
    pass
except Exception as e:
    LOGGER.debug("Could not instrument tcell_hooks: {e}".format(e=e))
    LOGGER.debug(e, exc_info=True)
