from ..exceptions import AuthAlreadyAssociated, AuthException, AuthForbidden


def pixelpin_auth_details(backend, details, response, *args, **kwargs):
    return {'details': dict(backend.get_user_details(response), **details)}


def pixelpin_auth_uid(backend, details, response, *args, **kwargs):
    return {'uid': backend.get_user_id(details, response)}


def auth_allowed(backend, details, response, *args, **kwargs):
    if not backend.auth_allowed(response, details):
        raise AuthForbidden(backend)


def pixelpin_auth_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    pixelpin_auth = backend.strategy.storage.user.get_pixelpin_auth(provider, uid)
    if pixelpin_auth:
        if user and pixelpin_auth.user != user:
            msg = 'This {0} account is already in use.'.format(provider)
            raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = pixelpin_auth.user
    return {'pixelpin_auth': pixelpin_auth,
            'user': user,
            'is_new': user is None,
            'new_association': pixelpin_auth is None}


def associate_user(backend, uid, user=None, pixelpin_auth=None, *args, **kwargs):
    if user and not pixelpin_auth:
        try:
            pixelpin_auth = backend.strategy.storage.user.create_pixelpin_auth(
                user, uid, backend.name
            )
        except Exception as err:
            if not backend.strategy.storage.is_integrity_error(err):
                raise
            # Protect for possible race condition, those bastard with FTL
            # clicking capabilities, check issue #131:
            #   https://github.com/omab/django-pixelpin_auth-auth/issues/131
            return pixelpin_auth_user(backend, uid, user, *args, **kwargs)
        else:
            return {'pixelpin_auth': pixelpin_auth,
                    'user': pixelpin_auth.user,
                    'new_association': True}


def associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same email address in the DB.

    This pipeline entry is not 100% secure unless you know that the providers
    enabled enforce email verification on their side, otherwise a user can
    attempt to take over another user account by using the same (not validated)
    email address on some provider.  This pipeline entry is disabled by
    default.
    """
    if user:
        return None

    email = details.get('email')
    if email:
        # Try to associate accounts registered with the same email address,
        # only if it's a single object. AuthException is raised if multiple
        # objects are returned.
        users = list(backend.strategy.storage.user.get_users_by_email(email))
        if len(users) == 0:
            return None
        elif len(users) > 1:
            raise AuthException(
                backend,
                'The given email address is associated with another account'
            )
        else:
            return {'user': users[0],
                    'is_new': False}


def load_extra_data(backend, details, response, uid, user, *args, **kwargs):
    pixelpin_auth = kwargs.get('pixelpin_auth') or \
             backend.strategy.storage.user.get_pixelpin_auth(backend.name, uid)
    if pixelpin_auth:
        extra_data = backend.extra_data(user, uid, response, details,
                                        *args, **kwargs)
        pixelpin_auth.set_extra_data(extra_data)
