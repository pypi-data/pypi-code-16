from flask import g, Blueprint, request
from flask_login import login_required, login_user

from pixelpin_auth_core.actions import do_auth, do_complete, do_disconnect
from pixelpin_auth_flask.utils import psa


pixelpin_auth = Blueprint('pixelpin_auth', __name__)


@pixelpin_auth.route('/login/<string:backend>/', methods=('GET', 'POST'))
@psa('pixelpin_auth.complete')
def auth(backend):
    return do_auth(g.backend)


@pixelpin_auth.route('/complete/<string:backend>/', methods=('GET', 'POST'))
@psa('pixelpin_auth.complete')
def complete(backend, *args, **kwargs):
    """Authentication complete view, override this view if transaction
    management doesn't suit your needs."""
    return do_complete(g.backend, login=do_login, user=g.user,
                       *args, **kwargs)


@pixelpin_auth.route('/disconnect/<string:backend>/', methods=('POST',))
@pixelpin_auth.route('/disconnect/<string:backend>/<int:association_id>/',
                   methods=('POST',))
@pixelpin_auth.route('/disconnect/<string:backend>/<string:association_id>/',
                   methods=('POST',))
@login_required
@psa()
def disconnect(backend, association_id=None):
    """Disconnects given backend from current logged in user."""
    return do_disconnect(g.backend, g.user, association_id)


def do_login(backend, user, pixelpin_auth_user):
    name = backend.strategy.setting('REMEMBER_SESSION_NAME', 'keep')
    remember = backend.strategy.session_get(name) or \
               request.cookies.get(name) or \
               request.args.get(name) or \
               request.form.get(name) or \
               False
    return login_user(user, remember=remember)
