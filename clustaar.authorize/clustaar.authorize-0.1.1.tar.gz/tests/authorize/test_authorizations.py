from clustaar.authorize import Authorizations, Action
import pytest


@pytest.fixture
def authorizations():
    return Authorizations(default_action="deny")


@pytest.fixture
def action():
    return Action(name="view_project")

class TestConstructor(object):
    def test_raises_exception_if_invalid_default_action(self):
        with pytest.raises(ValueError) as exc:
            Authorizations(default_action="invalid")

        assert str(exc.value) == "'invalid' is not a valid action, 'deny' and 'allow' are."
class TestGenerateError(object):
    def test_returns_an_exception(self, authorizations, action):
        exception = authorizations.generate_error(action, {})
        assert str(exception) == "Access denied for view_project ({})"


class TestDefaultGetAttr(object):
    def test_returns_false_if_default_action_is_deny(self, authorizations):
        assert not authorizations.can_view_project()

    def test_returns_true_if_default_action_is_allow(self):
        authorizations = Authorizations(default_action="allow")
        assert authorizations.can_view_project()

    def test_raises_exception_if_not_a_can_method(self, authorizations):
        with pytest.raises(AttributeError):
            authorizations.say_hello()
