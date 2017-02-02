"""PytSite Reload Package.
"""
# Public API
from ._api import reload, set_flag, get_flag

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _init():
    from pytsite import lang, console, permissions, http_api, events, assetman
    from . import _console_command, _eh, _http_api

    lang.register_package(__name__)
    console.register_command(_console_command.Reload())
    assetman.register_package(__name__)
    permissions.define_permission('pytsite.reload', 'pytsite.reload@reload_application_permission', 'app')

    http_api.handle('POST', 'reload', _http_api.post_reload, 'pytsite.reload@post_reload')

    events.listen('pytsite.router.dispatch', _eh.router_dispatch)


_init()
