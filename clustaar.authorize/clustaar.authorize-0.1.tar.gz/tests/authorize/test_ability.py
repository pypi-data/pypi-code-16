from clustaar.authorize import Ability, Authorizations, Action
import pytest


class AuthorizationsMock(Authorizations):
    def can_view_project(self, project_id):
        return False

    def can_list_projects(self):
        return True


@pytest.fixture
def ability():
    authorizations = AuthorizationsMock()
    return Ability(authorizations)


@pytest.fixture
def view_action():
    return Action(name="view_project")


@pytest.fixture
def list_action():
    return Action(name="list_projects")


class TestAuthorize(object):
    def test_raises_exception_if_not_authorized(self, ability, view_action):
        with pytest.raises(Exception):
            ability.authorize(view_action, project_id=1)

    def test_does_nothing_if_allowed(self, ability, list_action):
        ability.authorize(list_action)


class TestCan(object):
    def test_returns_true_if_authorized(self, ability, list_action):
        assert ability.can(list_action)

    def test_returns_false_if_not_authorized(self, ability, view_action):
        assert not ability.can(view_action, project_id=1)
