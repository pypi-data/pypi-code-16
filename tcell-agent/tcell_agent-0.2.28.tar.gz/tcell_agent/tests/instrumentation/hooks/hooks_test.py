import sys

if sys.version_info >= (3, 0):
    import unittest

    from types import ModuleType

    from mock import MagicMock, patch

    from tcell_agent.agent import TCellAgent
    from tcell_agent.instrumentation.hooks import _instrument


    class LoginRegisterLoginEvent(object):  # noqa
        @classmethod
        def send(cls,
                 status,
                 session_id,
                 user_agent,
                 referrer,
                 remote_addr,
                 header_keys,
                 user_id,
                 document_uri,
                 user_valid=None):
            pass


    class DjangoRegisterLoginEvent(object):  # noqa
        @classmethod
        def send(cls, status, django_request, user_id, session_id, user_valid=None):
            pass


    class FlaskRegisterLoginEvent(object):  # noqa
        @classmethod
        def send(cls, status, flask_request, user_id, session_id, user_valid=None):
            pass


    m_login = ModuleType("tcell_hooks.hooks.v1.login")  # noqa
    m_django = ModuleType("tcell_hooks.hooks.v1.frameworks.django.login")
    m_flask = ModuleType("tcell_hooks.hooks.v1.frameworks.flask.login")


    class HooksTest(unittest.TestCase):  # noqa
        @classmethod
        def setUpClass(cls):
            m_login.__file__ = m_login.__name__ + ".py"
            m_django.__file__ = m_django.__name__ + ".py"
            m_flask.__file__ = m_flask.__name__ + ".py"

            setattr(m_login, 'LOGIN_SUCCESS', "success")
            setattr(m_login, 'LOGIN_FAILURE', "failure")
            setattr(m_login, 'RegisterLoginEvent', LoginRegisterLoginEvent)
            setattr(m_django, 'RegisterLoginEvent', DjangoRegisterLoginEvent)
            setattr(m_flask, 'RegisterLoginEvent', FlaskRegisterLoginEvent)

            sys.modules[m_login.__name__] = m_login
            sys.modules[m_django.__name__] = m_django
            sys.modules[m_flask.__name__] = m_flask

            _instrument()

        @classmethod
        def tearDownClass(cls):
            del sys.modules[m_login.__name__]
            del sys.modules[m_django.__name__]
            del sys.modules[m_flask.__name__]

        def login_success_init_hooks_test(self):
            with patch.object(TCellAgent, 'send', return_value=None) as patched_send:
                LoginRegisterLoginEvent.send(
                    m_login.LOGIN_SUCCESS,
                    "124KDJFL3234",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                    "http://192.168.99.100:3000/",
                    "192.168.99.1",
                    ["HOST", "USER_AGENT", "REFERER"],
                    "tcell@tcell.io",
                    "/users/auth/doorkeeper/callbackuri")

                self.assertTrue(patched_send.called)
                args, _ = patched_send.call_args
                event = args[0]
                self.assertEqual(event['event_type'], 'login')
                self.assertSetEqual(set(event['header_keys']), set(['HOST', 'REFERER', 'USER_AGENT']))
                self.assertEqual(event['session'], '124KDJFL3234')
                self.assertEqual(event['event_name'], 'login-success')
                self.assertEqual(event['remote_addr'], '192.168.99.1')
                self.assertEqual(event['user_id'], 'tcell@tcell.io')
                self.assertEqual(event['user_agent'], 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...')

        def login_failure_init_hooks_test(self):
            with patch.object(TCellAgent, 'send', return_value=None) as patched_send:
                LoginRegisterLoginEvent.send(
                    m_login.LOGIN_FAILURE,
                    "124KDJFL3234",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                    "http://192.168.99.100:3000/",
                    "192.168.99.1",
                    ["HOST", "USER_AGENT", "REFERER"],
                    "tcell@tcell.io",
                    "/users/auth/doorkeeper/callbackuri")

                self.assertTrue(patched_send.called)
                args, _ = patched_send.call_args
                event = args[0]
                self.assertEqual(event['event_type'], 'login')
                self.assertSetEqual(set(event['header_keys']), set(['HOST', 'REFERER', 'USER_AGENT']))
                self.assertEqual(event['session'], '124KDJFL3234')
                self.assertEqual(event['event_name'], 'login-failure')
                self.assertEqual(event['remote_addr'], '192.168.99.1')
                self.assertEqual(event['user_id'], 'tcell@tcell.io')
                self.assertEqual(event['user_agent'], 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...')

        def django_login_success_init_hooks_test(self):
            django_request = MagicMock(
                'FakeRequest',
                META={
                    'REMOTE_ADDR': '192.168.99.1',
                    'HTTP_HOST': 'http://192.168.99.1',
                    'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...'})
            django_request.get_full_path = MagicMock(return_value='/users/auth/doorkeeper/callbackuri')

            with patch.object(TCellAgent, 'send', return_value=None) as patched_send:
                DjangoRegisterLoginEvent.send(
                    m_login.LOGIN_SUCCESS,
                    django_request,
                    "tcell@tcell.io",
                    "124KDJFL3234")

                self.assertTrue(patched_send.called)
                args, _ = patched_send.call_args
                event = args[0]
                self.assertEqual(event['event_type'], 'login')
                self.assertSetEqual(set(event['header_keys']), set(['HOST', 'USER_AGENT']))
                self.assertEqual(event['session'], '124KDJFL3234')
                self.assertEqual(event['event_name'], 'login-success')
                self.assertEqual(event['remote_addr'], '192.168.99.1')
                self.assertEqual(event['user_id'], 'tcell@tcell.io')
                self.assertEqual(event['user_agent'], 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...')

        def django_login_failure_init_hooks_test(self):
            django_request = MagicMock(
                'FakeRequest',
                META={
                    'REMOTE_ADDR': '192.168.99.1',
                    'HTTP_HOST': 'http://192.168.99.1',
                    'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...'})
            django_request.get_full_path = MagicMock(return_value='/users/auth/doorkeeper/callbackuri')

            with patch.object(TCellAgent, 'send', return_value=None) as patched_send:
                DjangoRegisterLoginEvent.send(
                    m_login.LOGIN_FAILURE,
                    django_request,
                    "tcell@tcell.io",
                    "124KDJFL3234")

                self.assertTrue(patched_send.called)
                args, _ = patched_send.call_args
                event = args[0]
                self.assertEqual(event['event_type'], 'login')
                self.assertSetEqual(set(event['header_keys']), set(['HOST', 'USER_AGENT']))
                self.assertEqual(event['session'], '124KDJFL3234')
                self.assertEqual(event['event_name'], 'login-failure')
                self.assertEqual(event['remote_addr'], '192.168.99.1')
                self.assertEqual(event['user_id'], 'tcell@tcell.io')
                self.assertEqual(event['user_agent'], 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...')

        def flask_login_success_init_hooks_test(self):
            flask_request = MagicMock(
                'FakeRequest',
                url='/users/auth/doorkeeper/callbackuri',
                environ={
                    'REMOTE_ADDR': '192.168.99.1',
                    'HTTP_HOST': 'http://192.168.99.1',
                    'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...'})

            with patch.object(TCellAgent, 'send', return_value=None) as patched_send:
                FlaskRegisterLoginEvent.send(
                    m_login.LOGIN_SUCCESS,
                    flask_request,
                    "tcell@tcell.io",
                    "124KDJFL3234")

                self.assertTrue(patched_send.called)
                args, _ = patched_send.call_args
                event = args[0]
                self.assertEqual(event['event_type'], 'login')
                self.assertSetEqual(set(event['header_keys']), set(['HOST', 'USER_AGENT']))
                self.assertEqual(event['session'], '124KDJFL3234')
                self.assertEqual(event['event_name'], 'login-success')
                self.assertEqual(event['remote_addr'], '192.168.99.1')
                self.assertEqual(event['user_id'], 'tcell@tcell.io')
                self.assertEqual(event['user_agent'], 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...')

        def flask_login_failure_init_hooks_test(self):
            flask_request = MagicMock(
                'FakeRequest',
                url='/users/auth/doorkeeper/callbackuri',
                environ={
                    'REMOTE_ADDR': '192.168.99.1',
                    'HTTP_HOST': 'http://192.168.99.1',
                    'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...'})

            with patch.object(TCellAgent, 'send', return_value=None) as patched_send:
                FlaskRegisterLoginEvent.send(
                    m_login.LOGIN_FAILURE,
                    flask_request,
                    "tcell@tcell.io",
                    "124KDJFL3234")

                self.assertTrue(patched_send.called)
                args, _ = patched_send.call_args
                event = args[0]
                self.assertEqual(event['event_type'], 'login')
                self.assertSetEqual(set(event['header_keys']), set(['HOST', 'USER_AGENT']))
                self.assertEqual(event['session'], '124KDJFL3234')
                self.assertEqual(event['event_name'], 'login-failure')
                self.assertEqual(event['remote_addr'], '192.168.99.1')
                self.assertEqual(event['user_id'], 'tcell@tcell.io')
                self.assertEqual(event['user_agent'], 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...')

        def unknown_status_init_hooks_test(self):
            mock_logger = MagicMock()
            mock_logger.error.return_value = None

            with patch.object(TCellAgent, 'send', return_value=None) as patched_send:
                with patch('tcell_agent.instrumentation.hooks.get_logger') as patched_get_logger:
                    patched_get_logger.return_value = mock_logger

                    LoginRegisterLoginEvent.send(
                        "blergh",
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertFalse(patched_send.called)
                    mock_logger.error.assert_called_once_with('Unkown login status: blergh')
