"""
Shaft Auth
"""

import signals
import logging
import exceptions
import flask_login
from flask import current_app
from shaft.exceptions import AppError
from shaft.core import get_installed_app_options
from shaft import (register_package,
                   utc_now,
                   get_config,
                   abort,
                   send_mail,
                   url_for,
                   views,
                   models,
                   utils,
                   request,
                   redirect,
                   flash,
                   session,
                   init_app)
from itsdangerous import (TimedJSONWebSignatureSerializer, BadData)
import models as auth_models
from flask_login import current_user

__version__ = "1.0.0"
__options__ = utils.dict_dot({})

register_package(__package__)


# USER ROLES

ROLES_SUPERADMIN = ["SUPERADMIN"]
ROLES_ADMIN = ROLES_SUPERADMIN + ["ADMIN"]
ROLES_MANAGER = ROLES_ADMIN + ["MANAGER"]
ROLES_CONTRIBUTOR = ROLES_MANAGER + ["EDITOR", "CONTRIBUTOR"]
ROLES_MODERATOR = ROLES_CONTRIBUTOR + ["MODERATOR"]


JWT_TTL = 3600
JWT_SALT = "shaft.contrib.auth"

TOKENIZATION_SALTS = {
    "verify-email": "auth:verify-email",
    "reset-password": "auth:reset-password",
    "email": "auth:email",
    "data": "auth:user:data"
}


# LOGIN MANAGER: Flask Login
login_manager = flask_login.LoginManager()
login_manager.login_message_category = "error"
init_app(login_manager.init_app)

@login_manager.user_loader
def load_user(userid):
    return models.AuthUser.get(userid)


def ___main(app):
    @app.before_request
    def force_password_change():
        _ = __options__.get("require_password_change_exclude_endpoints")
        _ = [] if not isinstance(_, list) else _

        exclude_endpoints = ["static", "ContactPage:index", "Index:index",
                             "AuthLogin:logout"] + _

        if current_user and current_user.is_authenticated:
            if request.endpoint \
                    and request.endpoint not in exclude_endpoints:
                if request.endpoint != "AuthAccount:change_password" \
                        and session_get_require_password_change():
                    flash("Password Change is required", "info")
                    return redirect(views.AuthAccount.change_password)


# ------------------------------------------------------------------------------

def is_authenticated():
    """ A shortcut to check if a user is authenticated """
    return current_user and current_user.is_authenticated


def not_authenticated():
    """ A shortcut to check if user not authenticated."""
    return not is_authenticated()


def get_random_password(length=8):
    return utils.generate_random_string(length)


# ------------------------------------------------------------------------------
# VISIBILITY:
# The methods below return bool that are meant be pass in the
# nav_title(visible=fn) `visible` args
#

def visible_to_roles(*roles):
    """
    This is a @nav_title specific function to set the visibility of menu based on
    roles
    :param roles:
    :return: callback fn
    """
    if is_authenticated():
        return True if current_user.has_any_roles(*roles) else False
    return False


# Alias
def visible_to_superadmins():
    return visible_to_roles(*ROLES_SUPERADMIN)


def visible_to_admins():
    return visible_to_roles(*ROLES_ADMIN)


def visible_to_managers():
    return visible_to_roles(*ROLES_MANAGER)


def visible_to_contributors():
    return visible_to_roles(*ROLES_CONTRIBUTOR)


def visible_to_moderators():
    return visible_to_roles(*ROLES_MODERATOR)


def visible_to_authenticated():
    return is_authenticated()


def visible_to_non_authenticated():
    return not_authenticated()

# ------------------------------------------------------------------------------

# TOKENIZATION


def get_jwt_secret():
    secret_key = __options__.get("jwt_secret") or get_config("JWT_SECRET") or get_config("SECRET_KEY")
    if not secret_key:
        raise exceptions.AuthError("Missing config JWT/SECRET_KEY")
    return secret_key


def make_user_jwt(user, expires_in=None):
    """
    Create a secure timed JWT token that can be passed. It save the user id,
    which later will be used to retrieve the data

    :param user: AuthUser, the user's object
    :param expires_in: - time in second for the token to expire
    :return: string
    """
    secret_key = get_jwt_secret()
    s = utils.sign_jwt(data={"id": user.id},
                       secret_key=secret_key,
                       salt=JWT_SALT,
                       expires_in=expires_in or JWT_TTL)
    return s


def get_user_jwt(token=None):
    """
    Return the user associated to the token, otherwise it will return None.
    If token is not provided, it will pull it from the headers: Authorization

    Exception:
    Along with AuthError, it may
    :param token:
    :return: User
    """

    if not token:
        if not 'Authorization' in request.headers:
            raise exceptions.AuthError(
                "Missing Authorization Bearer in headers")
        data = request.headers['Authorization'].encode('ascii', 'ignore')
        token = str.replace(str(data), 'Bearer ', '').strip()

    secret_key = get_jwt_secret()

    s = utils.unsign_jwt(token=token,
                         secret_key=secret_key,
                         salt=JWT_SALT)
    if "id" not in s:
        raise exceptions.AuthError("Invalid Authorization Bearer Token")

    return get_user(int(s["id"]))


def make_user_token(user, expires_in, salt):
    """
    Make an auth url safe token. usually to do some account action. It will
    connect to the UserLogin table
    It will set the user
    :param user: AuthUser
    :param expires_in:
    :param salt:
    :return:
    """
    secret_key = get_jwt_secret()
    return utils.sign_url_safe(user.id,
                               secret_key=secret_key,
                               salt=TOKENIZATION_SALTS[salt],
                               expires_in=expires_in)


def get_user_token(token, salt):
    """
    Get the user token and return the user object .
    :param token:
    :param salt:
    :return: int : User
    """
    secret_key = get_jwt_secret()
    data = utils.unsign_url_safe(token,
                                 secret_key=secret_key,
                                 salt=TOKENIZATION_SALTS[salt])
    if data is None:
        raise exceptions.AuthError("Invalid Token")
    return get_user(int(data))



# ------------------------------------------------------------------------------
# SIGNUP + LOGIN


def get_user(id):
    """
    To get a user by id
    :param id:
    :return: AuthUser object
    """
    return models.AuthUser.get(id)


def get_user_login(id):
    """
    To get a user by id
    :param id:
    :return: AuthUserLogin object
    """
    return models.AuthUserLogin.get(id)


def get_user_by_login_email(email):
    """
    Get the user by login email
    :param email:
    :return:  AuthUser
    """
    userl = models.AuthUserLogin.get_by_email(email)
    return userl.user if userl else None


def login(email, password, require_verified_email=False, session=True):
    """
    To login with email and password
    Additionally, it may require_th
    :param email:
    :param password:
    :param require_verified_email:
    :param session:
    :return: on_login signal
    """

    def cb():
        userl = models.AuthUserLogin.get_by_email(email)
        if userl and userl.password_hash \
                and userl.password_matched(password):
            if require_verified_email and not userl.email_verified:
                raise exceptions.VerifyEmailError()
            user = userl.user
            user.update(last_login=utc_now())
            if session:

                flask_login.login_user(user)
            return user
        return None

    return signals.on_login(cb)


def register(email, password, name, role_name="MEMBER"):
    """
    Register by email
    :param email:
    :param password:
    :param name:
    :param role_name:
    :return:
    """

    def cb():
        role = models.AuthRole.get_by_name(role_name)
        if not role:
            raise exceptions.AuthError("Invalid ROLE selected")

        user_login = models \
            .AuthUserLogin.new(provider="email",
                               email=email,
                               password=password.strip(),
                               name=name,
                               role=role)
        return user_login.user
    return signals.on_register(cb)


def change_login(user, email):
    """
    Change user's login email
    :param user:
    :param email:
    :return:
    """

    def cb():
        user_login = user.get_login()
        return user_login.change_email(email)
    return signals.on_login_changed(cb)


def update_info(user, **kwargs):
    """
    Change user's login email
    :param user:
    :param email:
    :return:
    """

    def cb():
        profile_image = kwargs.pop("profile_image", None)
        user.update(**kwargs)
        if profile_image:
            user.update_profile_image(url=profile_image.pop("url", None),
                                      object_name=profile_image.pop("object_name", None),
                                      **profile_image)
        return user
    return signals.on_info_updated(cb)


def change_password(user, password, password_confirm=None):
    """
    Change a user's password
    :param user:
    :param password:
    :param password_confirm:
    :return:
    """

    def cb():
        user_login = user.get_login()
        if not utils.is_password_valid(password):
            raise exceptions.AuthError("Invalid Password")
        if password_confirm is not None and password != password_confirm:
            raise exceptions.AuthError("Passwords don't match")
        return user_login.change_password(password)

    return signals.on_password_changed(cb)


def reset_password(user):
    """
    Return the new random password that has been reset
    :param user_login: AuthUserLogin
    :return: string - the new password
    """

    def cb():
        user_login = user.get_login()
        return user_login.change_password(get_random_password())
    return signals.on_password_reset(cb)


# ------------------------------------------------------------------------------
# EMAIL SENDING


def _url_for_email(endpoint, base_url=None, **kw):
    """
    Create an external url_for by using a custom base_url different from the domain we
    are on
    :param endpoint:
    :param base_url:
    :param kw:
    :return:
    """
    base_url = base_url or get_config("MAIL_EXTERNAL_BASE_URL")
    _external = True if not base_url else False
    url = url_for(endpoint, _external=_external, **kw)
    if base_url and not _external:
        url = "%s/%s" % (base_url.strip("/"), url.lstrip("/"))
    return url


def send_password_reset_email(user=None,
                              email=None,
                              base_url=None,
                              template=None,
                              method=None,
                              view_class=None,
                              **kw):
    """
    Reset a password and send email
    :param user: AuthUser
    :param email: str - The auth user login email
    :param base_url: str - By default it will use the current url, base_url will allow custom url
    :param template: str - The email template
    :param method: str - token or email - The method to reset the password
    :param view_class: obj - The view instance of the login
    :param kwargs: Any data to pass
    :return:
    """
    view = view_class or views.auth.Login
    if email and not user:
        user = get_user_by_login_email(email)
    if not user:
        raise exceptions.AuthError("Invalid account. Unable to send email")
    user_login = user.get_login()
    if user_login.provider != models.AuthUserLogin.TYPE_EMAIL:
        raise exceptions.AuthError(
            "Invalid login type. Must be the type of email to be sent email to")

    method = method or __options__.get("reset_password_method") or "TOKEN"
    email_template = template \
                     or __options__.get("reset_password_email_template") \
                     or "reset-password.txt"
    new_password = None

    if method.upper() == "TOKEN":
        expires_in = __options__.get("reset_password_token_ttl", 1) or 1
        token = make_user_token(user, expires_in=expires_in, salt="reset-password")
        action_token = user.sign_data("reset-password", expires_in=expires_in)
        url = _url_for_email(getattr(view, "reset_password"),
                             base_url=base_url,
                             token=token,
                             action_token=action_token)
    else:
        new_password = reset_password(user)
        url = _url_for_email(getattr(view, "login"),
                             base_url=base_url)

    send_mail(template=email_template,
              to=user_login.email,
              user=user.email_data,
              action={
                  "reset_method": method.upper(),
                  "url": url,
                  "new_password": new_password
              },
              data=kw)


def send_email_verification_email(user,
                                  base_url=None,
                                  template=None,
                                  view_class=None,
                                  **kw):

    email_template = template \
                     or __options__.get("verify_email_template") \
                     or "verify-email.txt"

    user_login = user.get_login()
    url = _create_verify_email_token_url(user,
                                         base_url=base_url,
                                         view_class=view_class)

    send_mail(template=email_template,
              to=user_login.email,
              user=user.email_data,
              action={
                  "url": url
              },
              data=kw)


def send_registration_welcome_email(user,
                                    base_url=None,
                                    template=None,
                                    view_class=None,
                                    **kw):

    verify_email = __options__.get("verify_email") or False
    email_template = template \
                     or __options__.get("verify_register_email_template") \
                     or "verify-register-email.txt"

    user_login = user.get_login()
    url = _create_verify_email_token_url(user,
                                         base_url=base_url,
                                         view_class=view_class)

    send_mail(template=email_template,
              to=user_login.email,
              user=user.email_data,
              action={
                  "require_email_verification": verify_email,
                  "url": url
              },
              data=kw)


def _create_verify_email_token_url(user, base_url=None, view_class=None):
    """
    To create a verify email token url
    :param user: (object) AuthUser
    :param base_url: a base_url to use instead of the native one
    :param view_class: (obj) the view class, to allow build the url
    :return: string
    """
    view = view_class or views.auth.Login
    options = _get_app_options()
    expires_in = options.get("verify_email_token_ttl") or (60 * 24)

    user_login = user.get_login()
    user_login.set_email_verified(False)
    token = make_user_token(user, expires_in=expires_in, salt="verify-email")
    action_token = user.sign_data("verify-email", expires_in=expires_in)
    return _url_for_email(getattr(view, "verify_email"),
                          token=token,
                          action_token=action_token,
                          base_url=base_url)


def session_set_require_password_change(change=True):
    session["auth:require_password_change"] = change


def session_get_require_password_change():
    return session.get("auth:require_password_change")


# ------------------------------------------------------------------------------
# CLI
from shaft.cli import CLI


class AuthCLI(CLI):
    def __init__(self, command, click):
        @command("auth:create-super-admin")
        @click.argument("email")
        def create_super_admin(email):
            """
            To create a super admin by providing the email address
            """
            print("-" * 80)
            print("Shaft Auth: Create Super Admin")
            print("Email: %s" % email)
            try:
                password = get_random_password()
                user = register(email=email, password=password,
                                name="SuperAdmin", role_name="Superadmin")
                user.update(require_password_change=True)

                print("Password: %s" % password)
            except Exception as e:
                print("ERROR: %s" % e)

            print("Done!")

        @command("auth:reset-password")
        @click.argument("email")
        def reset_password(email):
            """
            To reset password by email
            """
            print("-" * 80)
            print("Shaft Auth: Reset Password")
            try:
                ul = models.AuthUserLogin.get_by_email(email)

                if not ul:
                    raise Exception("Email '%s' doesn't exist" % email)
                print(ul.email)
                password = get_random_password()
                ul.change_password(password)
                ul.update(require_password_change=True)
                print("Email: %s" % email)
                print("New Password: %s" % password)
            except Exception as e:
                print("ERROR: %s" % e)

            print("Done!")

        @command("auth:user-info")
        @click.option("--email")
        @click.option("--id")
        def reset_password(email=None, id=None):
            """
            Get the user info by email or ID
            """
            print("-" * 80)
            print("Shaft Auth: User Info")
            print("")
            try:
                if email:
                    ul = models.AuthUserLogin.get_by_email(email)
                    if not ul:
                        raise Exception("Invalid Email address")
                    user_info = ul.user
                elif id:
                    user_info = models.AuthUser.get(id)
                    if not user_info:
                        raise Exception("Invalid User ID")

                k = [
                    ("ID", "id"), ("Name", "name"),
                    ("First Name", "first_name"),
                    ("Last Name", "last_name"), ("Signup", "created_at"),
                    ("Last Login", "last_login"),
                    ("Signup Method", "register_method"),
                    ("Is Active", "is_active")
                ]
                print("Email: %s" % user_info.get_email_login().email)
                for _ in k:
                    print("%s : %s" % (_[0], getattr(user_info, _[1])))

            except Exception as e:
                print("ERROR: %s" % e)

            print("")
            print("Done!")


# ---

from .decorators import *
