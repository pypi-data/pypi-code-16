from ..models import User
from .actions import BaseActionTest


class LoginActionTest(BaseActionTest):
    def test_login(self):
        self.do_login()

    def test_login_with_partial_pipeline(self):
        self.do_login_with_partial_pipeline()

    def test_fields_stored_in_session(self):
        self.strategy.set_settings({
            'pixelpin_auth_FIELDS_STORED_IN_SESSION': ['foo', 'bar']
        })
        self.strategy.set_request_data({'foo': '1', 'bar': '2'}, self.backend)
        self.do_login()
        self.assertEqual(self.strategy.session_get('foo'), '1')
        self.assertEqual(self.strategy.session_get('bar'), '2')

    def test_redirect_value(self):
        self.strategy.set_request_data({'next': '/after-login'}, self.backend)
        redirect = self.do_login(after_complete_checks=False)
        self.assertEqual(redirect.url, '/after-login')

    def test_login_with_invalid_partial_pipeline(self):
        def before_complete():
            partial_token = self.strategy.session_get('partial_pipeline_token')
            partial = self.strategy.storage.partial.load(partial_token)
            partial.data['backend'] = 'foobar'
        self.do_login_with_partial_pipeline(before_complete)

    def test_new_user(self):
        self.strategy.set_settings({
            'pixelpin_auth_NEW_USER_REDIRECT_URL': '/new-user'
        })
        redirect = self.do_login(after_complete_checks=False)
        self.assertEqual(redirect.url, '/new-user')

    def test_inactive_user(self):
        self.strategy.set_settings({
            'pixelpin_auth_INACTIVE_USER_URL': '/inactive'
        })
        User.set_active(False)
        redirect = self.do_login(after_complete_checks=False)
        self.assertEqual(redirect.url, '/inactive')

    def test_invalid_user(self):
        self.strategy.set_settings({
            'pixelpin_auth_LOGIN_ERROR_URL': '/error',
            'pixelpin_auth_PIPELINE': (
                'pixelpin_auth_core.pipeline.pixelpin_auth.pixelpin_auth_details',
                'pixelpin_auth_core.pipeline.pixelpin_auth.pixelpin_auth_uid',
                'pixelpin_auth_core.pipeline.pixelpin_auth.auth_allowed',
                'pixelpin_auth_core.pipeline.pixelpin_auth.pixelpin_auth_user',
                'pixelpin_auth_core.pipeline.user.get_username',
                'pixelpin_auth_core.pipeline.user.create_user',
                'pixelpin_auth_core.pipeline.pixelpin_auth.associate_user',
                'pixelpin_auth_core.pipeline.pixelpin_auth.load_extra_data',
                'pixelpin_auth_core.pipeline.user.user_details',
                'pixelpin_auth_core.tests.pipeline.remove_user'
            )
        })
        redirect = self.do_login(after_complete_checks=False)
        self.assertEqual(redirect.url, '/error')
