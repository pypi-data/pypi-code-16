""" PytSite Authentication and Authorization.
"""
# Public API
from . import _error as error, _model as model, _driver as driver, _widget as widget
from ._api import get_current_user, get_user_statuses, get_user, create_user, get_role, get_sign_in_form, \
    register_auth_driver, user_nickname_rule, sign_in, get_auth_driver, create_role, get_sign_in_url, get_sign_out_url,\
    verify_password, hash_password, sign_out, get_access_token_info, switch_user, get_anonymous_user, \
    get_system_user, get_users, get_storage_driver, count_users, count_roles, get_first_admin_user, get_roles, \
    get_user_modify_form, base_path, switch_user_to_system, switch_user_to_anonymous, restore_user

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def __init():
    """Init wrapper.
    """
    from pytsite import assetman, events, tpl, lang, router, robots, console, http_api, permissions
    from ._console_command import Passwd as AuthConsoleCommand
    from . import _eh, _http_api

    # Resources
    tpl.register_package(__name__)
    lang.register_package(__name__)
    assetman.register_package(__name__)
    assetman.add('pytsite.auth@js/auth.js', permanent=True)

    # Module permission group
    permissions.define_group('security', 'pytsite.auth@security')

    # HTTP API handlers
    http_api.handle('POST', 'auth/access-token', _http_api.post_access_token,
                    'pytsite.auth@post_access_token')
    http_api.handle('GET', 'auth/access-token/<token>', _http_api.get_access_token,
                    'pytsite.auth@get_access_token')
    http_api.handle('DELETE', 'auth/access-token/<token>', _http_api.delete_access_token,
                    'pytsite.auth@delete_access_token')
    http_api.handle('GET', 'auth/user/<uid>', _http_api.get_user,
                    'pytsite.auth@get_user')
    http_api.handle('PATCH', 'auth/user/<uid>', _http_api.patch_user,
                    'pytsite.auth@patch_user')

    # ???
    http_api.handle('PATCH', 'auth/follow/<uid>', _http_api.patch_follow, 'pytsite.auth@patch_follow')

    # Common routes
    bp = base_path()
    router.add_rule(bp + '/sign-in/<driver>', 'pytsite.auth@sign_in')
    router.add_rule(bp + '/sign-in/<driver>/post', 'pytsite.auth@sign_in_submit', methods='POST')
    router.add_rule(bp + '/sign-out/<driver>', 'pytsite.auth@sign_out')
    router.add_rule(bp + '/profile/<nickname>', 'pytsite.auth@profile_view')
    router.add_rule(bp + '/profile/<nickname>/edit', 'pytsite.auth@profile_edit', filters='pytsite.auth@f_authorize')
    router.add_rule(bp + '/profile/<nickname>/edit/submit', 'pytsite.auth@profile_edit_submit', methods='POST')

    # Template engine globals
    tpl.register_global('auth_current_user', get_current_user)
    tpl.register_global('auth_sign_in_url', get_sign_in_url)
    tpl.register_global('auth_sign_out_url', get_sign_out_url)

    # Event handlers
    events.listen('pytsite.setup', _eh.setup)
    events.listen('pytsite.router.dispatch', _eh.router_dispatch, priority=-9999)
    events.listen('pytsite.router.response', _eh.router_response)

    # Console commands
    console.register_command(AuthConsoleCommand())

    # robots.txt rules
    robots.disallow(bp + '/')


__init()
