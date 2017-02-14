import datetime
import uuid
import arrow
import exceptions
from flask_login import fresh_login_required
import logging
import exceptions
from flask_login import (LoginManager,
                         login_user,
                         current_user,
                         fresh_login_required)
from shaft import (Shaft,
                   _,
                   models,
                   page_meta,
                   request,
                   redirect,
                   flash_success,
                   flash_error,
                   flash_info,
                   abort,
                   recaptcha,
                   storage,
                   decorators as shaft_deco,
                   exceptions as shaft_exc,
                   exceptions,
                   utils,
                   paginate,
                   views
                   )


from shaft.contrib.auth import (is_authenticated,
                                not_authenticated,
                                send_password_reset_email,
                                send_email_verification_email,
                                send_registration_welcome_email,
                                session_set_require_password_change,
                                visible_to_managers,
                                get_user_token,
                                login,
                                register,
                                exceptions,
                                change_password,
                                change_login,
                                update_info,
                                __options__ as auth_options,
                                login_manager,
                                decorators as deco
                                )

__options__ = utils.dict_dot({})


def main(**kwargs):

    options = kwargs.get("options", {})
    nav_title_partial = "AuthAccount/nav_title_partial.html"
    nav_kwargs = kwargs.get("nav_menu", {})
    verify_email = options.get("verify_email") or False

    # @shaft_deco.nav_title(
    #     title=nav_kwargs.pop("title", "My Account") or "My Account",
    #     visible=is_authenticated,
    #     css_id=nav_kwargs.pop("css_id", "auth-account-menu"),
    #     css_class=nav_kwargs.pop("css_class", "auth-account-menu"),
    #     align_right=nav_kwargs.pop("align_right", True),
    #     title_partial=nav_kwargs.pop("title_partial", nav_title_partial),
    #     **nav_kwargs)


class Login(Shaft):

    @classmethod
    def _register(cls, app, **kwargs):

        # Late Binding
        __options__.setdefault("login_view", "main.Index:index")
        __options__.setdefault("logout_view", "main.Index:index")
        __options__.setdefault("login_message", "Please log in to access this page.")
        __options__.setdefault("login_message_category", "info")

        # Nav Title
        nav = __options__.get("login.nav", {})
        nav.setdefault("title", None)
        nav.setdefault("order", 100)
        nav.setdefault("position", "right")
        nav.setdefault("title", _("Account"))
        nav["visible"] = not_authenticated
        shaft_deco.nav_title.add(nav.pop("title"), cls, **nav)

        # Route
        kwargs["base_route"] = __options__.get("login.route", "/")

        # Set auth options
        auth_options.update(__options__)

        # Login Manager
        login_manager.login_view = "auth.Login:login"
        login_manager.login_message = __options__.get("login_message")
        login_manager.login_message_category = __options__.get("login_message_category")

        super(cls, cls)._register(app, **kwargs)

    @shaft_deco.nav_title("Login", visible=not_authenticated)
    @shaft_deco.allow_post_get
    @deco.login_not_required
    @deco.require_login_allowed
    @deco.logout_user
    def login(self):
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            try:
                if not email or not password:
                    raise shaft_exc.AppError("Email or Password is empty")

                user = login(email=email,
                             password=password,
                             require_verified_email=__options__.get("verify_email"))
                if not user:
                    raise shaft_exc.AppError("Email or Password is invalid")

                userl = user.get_login()
                if userl.require_password_change is True:
                    flash_info("Password change is required")
                    session_set_require_password_change(True)

                    return redirect(views.auth.user_account.Main.change_password)

                return redirect(request.form.get("next") or __options__.get("login_view"))

            except exceptions.VerifyEmailError as ve:
                return redirect(self.login, email=email, v="1")
            except (shaft_exc.AppError, exceptions.AuthError) as ae:
                flash_error(str(ae))
            except Exception as e:
                logging.exception(e)
                flash_error("Unable to login")

            return redirect(self.login, next=request.form.get("next"))

        page_meta("Login")
        return {
            "email": request.args.get("email"),
            "login_url_next": request.args.get("next", ""),
            "allow_register": __options__.get("allow_register"),
            "show_verification_message": True if request.args.get("v") == "1" else False
        }

    @shaft_deco.nav_title("Logout", visible=False)
    @deco.login_not_required
    @shaft_deco.allow_get
    @deco.logout_user
    def logout(self):
        session_set_require_password_change(False)
        return redirect(__options__.get("logout_view") or self.login)

    @shaft_deco.nav_title("Lost Password")
    @shaft_deco.allow_post_get
    @deco.login_not_required
    # @deco.require_login_allowed
    @deco.logout_user
    def lost_password(self):
        page_meta("Lost Password")

        if request.method == "POST":
            email = request.form.get("email")
            user_l = models.AuthUserLogin.get_by_email(email)
            if user_l:
                send_password_reset_email(user=user_l.user, view_class=self)
                flash_success("A new password has been sent to '%s'" % email)
                return redirect(self.login)
            else:
                flash_error("Invalid email address or email doesn't exist")
                return redirect(self.lost_password)

    @shaft_deco.nav_title("Signup", visible=not_authenticated())
    @shaft_deco.allow_post_get
    @deco.login_not_required
    # @deco.require_login_allowed
    # @deco.require_register_allowed
    @shaft_deco.template("auth/login/register.jade")
    @deco.logout_user
    def register(self):
        """ Registration """
        page_meta("Register")

        if request.method == "POST":
            try:
                if not recaptcha.verify():
                    raise shaft_exc.AppError("Invalid Security code")

                name = request.form.get("name", "").strip()
                email = request.form.get("email", "").strip()
                password = request.form.get("password", "").strip()
                password_confirm = request.form.get("password_confirm", "").strip()

                if not name:
                    raise shaft_exc.AppError("Name is required")
                elif not password or password != password_confirm:
                    raise shaft_exc.AppError("Passwords don't match")
                else:
                    user = register(email=email, password=password, name=name)
                    if __options__.get("verify_email"):
                        send_registration_welcome_email(user, view_class=self)
                        flash_success("A welcome email containing a confirmation link has been sent")
                    return redirect(request.form.get("next") or __options__.get("login_view"))
            except (shaft_exc.AppError, exceptions.AuthError) as ex:
                flash_error(str(ex))
            except Exception as e:
                logging.exception(e)
                flash_error("Unable to register")

            return redirect(self.register, next=request.form.get("next"))

        return dict(login_url_next=request.args.get("next", ""), )

    @shaft_deco.nav_title("Reset Password", visible=False)
    @shaft_deco.route("/reset-password/<token>/<action_token>/", methods=["POST", "GET"])
    @deco.login_not_required
    # @deco.require_login_allowed
    @shaft_deco.template("auth/login/reset_password.jade")
    @deco.logout_user
    def reset_password(self, token, action_token):
        """Reset the user password. It was triggered by LOST-PASSWORD """
        try:
            page_meta("Reset Password")

            user = get_user_token(token, "reset-password")
            if not user or not user.signed_data_match(action_token, "reset-password"):
                raise shaft_exc.AppError("Verification Invalid!")

            if request.method == "POST":
                password = request.form.get("password", "").strip()
                password_confirm = request.form.get("password_confirm", "").strip()
                if not password or password != password_confirm:
                    raise exceptions.AuthError("Password is missing or passwords don't match")

                user_login = user.get_login()
                user_login.change_password(password)
                user_login.set_email_verified(True)
                session_set_require_password_change(False)
                flash_success("Password updated successfully!")
                return redirect(__options__.get("login_view") or self.login)

            return {"token": token, "action_token": action_token}

        except (shaft_exc.AppError, exceptions.AuthError) as ex:
            flash_error(str(ex))
        except Exception as e:
            logging.exception(e)
            flash_error("Unable to reset password")
        return redirect(self.login)

    @shaft_deco.nav_title("Confirm Email", visible=False)
    @shaft_deco.allow_post_get
    @deco.login_not_required
    # @deco.require_login_allowed
    @shaft_deco.template("auth/login/request_email_verification.jade")
    @deco.logout_user
    def request_email_verification(self):
        """"""
        if not __options__.get("verify_email"):
            return redirect(self.login)

        if request.method == "POST":
            email = request.form.get("email")
            if email and utils.is_email_valid(email):
                userl = models.AuthUserLogin.get_by_email(email)
                if userl:
                    if not userl.email_verified:
                        send_email_verification_email(userl.user, view_class=self)
                        flash_success("A verification email has been sent to %s" % email)
                    else:
                        flash_success("Your account is already verified")
                    return redirect(self.login, email=email)
            flash_error("Invalid account")
            return redirect(self.request_email_verification, email=email)

        page_meta("Request Email Verification")
        return {
            "email": request.args.get("email"),
        }

    # @deco.require_login_allowed
    @deco.login_not_required
    @shaft_deco.route("/verify-email/<token>/<action_token>/")
    @deco.logout_user
    def verify_email(self, token, action_token):
        """ To verify an email, it accepts a user token and action token.
         Triggered by confirm_email or admin
         """
        try:
            user = get_user_token(token, "verify-email")
            if not user or not user.signed_data_match(action_token, "verify-email"):
                raise shaft_exc.AppError("Verification Invalid!")
            else:
                user.get_login().set_email_verified(True)
                flash_success("Account verified. You can now login")
                return redirect(self.login, email=user.email)
        except Exception as e:
            logging.exception(e)
            flash_error("Verification Failed!")
        return redirect(self.login)

@deco.login_required
class Account(Shaft):

    @classmethod
    def _register(cls, app, **kwargs):

        # Nav
        nav = __options__.get("account.nav", {})
        nav.setdefault("title", None)
        nav.setdefault("order", 100)
        nav["visible"] = is_authenticated
        nav["position"] = "right"
        title = nav.pop("title") or _("My Account")

        # Custom Nav Title
        # Since Title can also be a callback function
        # We can do some customization to display a more fun account menu
        # Specially in the top nav
        custom_nav_title = __options__.get("account.custom_nav_title")
        if __options__.get("account.set_custom_nav_title") and custom_nav_title:
            def custom_nav():
                if is_authenticated():
                    return custom_nav_title.format(USER_NAME=current_user.name,
                                                   USER_EMAIL=current_user.login_email,
                                                   USER_PROFILE_IMAGE_URL=current_user.profile_image_url)
            title = custom_nav

        # Set the nav title
        shaft_deco.nav_title.add(title, cls, **nav)

        # Route
        kwargs["base_route"] = __options__.get("account.route", "/account/")

        super(cls, cls)._register(app, **kwargs)

    def _assert_current_password(self):
        """Assert the password to make sure it matches the current user """

        user_login = current_user.get_login()
        password = request.form.get("current_password")
        if not user_login.password_matched(password):
            raise exceptions.AuthError("Invalid password")

    @shaft_deco.nav_title("Logout", endpoint="auth.Login:logout", order=100)
    def _(self): pass

    @shaft_deco.nav_title("Account Info", order=1)
    def account_info(self):
        page_meta("Account Info")
        return {
            "__USER_ACCOUNT_FORM__": "auth/Account/edit-forms.jade"
        }


    @shaft_deco.allow_post
    def update_login(self):
        """Update the login email"""
        try:
            self._assert_current_password()
            email = request.form.get("email")
            change_login(current_user, email)
            flash_success(_("Login Email changed successfully!"))
        except exceptions.AuthError as ex:
            flash_error(str(ex))
        except Exception as e:
            logging.exception(e)
            flash_error(_("Unable to change email"))
        return redirect(self.account_info)

    @shaft_deco.allow_post
    def update_password(self):
        """Change password """
        try:
            self._assert_current_password()
            password = request.form.get("password", "").strip()
            password_confirm = request.form.get("password_confirm", "").strip()
            change_password(current_user, password, password_confirm)
            flash_success(_("Your password updated successfully!"))
        except exceptions.AuthError as ex:
            flash_error(str(ex))
        except Exception as e:
            logging.exception(e)
            flash_error(_("Unable to update password"))
        return redirect(self.account_info)

    @shaft_deco.allow_post
    def update_info(self):
        """Update basic account info"""
        try:
            name = request.form.get("name", "")
            file = request.files.get("file")
            kwargs = {}
            if file:
                my_photo = storage.upload(file,
                                          name=utils.guid(),
                                          prefix="profile-images/",
                                          allowed_extensions=["jpg", "jpeg", "png", "gif"])
                if my_photo:
                    kwargs["profile_image"] = {
                        "object_name": my_photo.name,
                        "url": my_photo.url,
                        "path": my_photo.path,
                        "provider": my_photo.provider_name
                    }
            kwargs["name"] = name

            update_info(current_user, **kwargs)
            flash_success(_("Info updated successfully!"))
        except exceptions.AuthError as ex:
            flash_error(str(ex))
        except Exception as e:
            logging.exception(e)
            flash_error(_("Unable to update info"))
        return redirect(self.account_info)

    @shaft_deco.nav_title("Setup Login", visible=False)
    @shaft_deco.allow_post_get
    def setup_login(self):
        return
        user_login = current_user.user_login("email")
        if user_login:
            return redirect(self.account_info)

        if request.method == "POST":
            try:
                email = request.form.get("email")
                password = request.form.get("password")
                password2 = request.form.get("password2")

                if not password.strip() or password.strip() != password2.strip():
                    raise exceptions.AuthError("Passwords don't match")
                else:
                    new_login = models.AuthUserLogin.new(login_type="email",
                                                         user_id=current_user.id,
                                                         email=email,
                                                         password=password.strip())
                    if verify_email:
                        send_registration_welcome_email(new_login.user)
                        flash_success("A welcome email containing a confirmation link has been sent to your email")
                        return redirect(self.account_info)
            except exceptions.AuthError as ex:
                flash_error(ex.message)
                return redirect(self.setup_login)
            except Exception as e:
                logging.exception(e)
                flash_error("Unable to setup login")
                return redirect(self)

@deco.login_required
@deco.accepts_manager_roles
class Admin(Shaft):

    @classmethod
    def _register(cls, app, **kwargs):

        # Nav
        nav = __options__.get("admin.nav", {})
        nav.setdefault("title", None)
        nav.setdefault("order", 100)
        nav["visible"] = visible_to_managers
        title = nav.pop("title") or _("User Admin")
        shaft_deco.nav_title.add(title, cls, **nav)

        # Route
        kwargs["base_route"] = __options__.get("admin.route", "/admin/users/")

        super(cls, cls)._register(app, **kwargs)


    def _confirm_password(self):
        user_login = current_user.user_login("email")
        password = request.form.get("confirm-password")
        if not user_login.password_matched(password):
            raise exceptions.AuthError("Invalid password")
        return True

    @classmethod
    def _user_roles_options(cls):
        _r = models.AuthRole.query()\
            .filter(models.AuthRole.level <= current_user.role.level)\
            .order_by(models.AuthRole.level.desc())
        return [(r.id, r.name.upper()) for r in _r]

    @shaft_deco.nav_title("All Users")
    def index(self):

        page_meta("All Users")

        include_deleted = True if request.args.get("include-deleted") == "y" else False
        name = request.args.get("name")
        email = request.args.get("email")
        role = request.args.get("role")
        sorting = request.args.get("sorting", "name__asc")
        users = models.AuthUser.query(include_deleted=include_deleted)
        users = users.join(models.AuthRole).filter(models.AuthRole.level <= current_user.role.level)

        if name:
            users = models.AuthUser.search_by_name(users, name)
        if email:
            users = users.join(models.AuthUserLogin).filter(models.AuthUserLogin.email.contains(email))
        if role:
            users = users.filter(models.AuthUser.role_id == int(role))
        if sorting and "__" in sorting:
            col, dir = sorting.split("__", 2)
            if dir == "asc":
                users = users.order_by(getattr(models.AuthUser, col).asc())
            else:
                users = users.order_by(getattr(models.AuthUser, col).desc())

        users = paginate(users)

        sorting = [("name__asc", "Name ASC"),
                   ("name__desc", "Name DESC"),
                   ("email__asc", "Email ASC"),
                   ("email__desc", "Email DESC"),
                   ("created_at__asc", "Signup ASC"),
                   ("created_at__desc", "Signup DESC"),
                   ("last_login__asc", "Login ASC"),
                   ("last_login__desc", "Login DESC")]

        return dict(user_roles_options=self._user_roles_options(),
                    sorting_options=sorting,
                    users=users,
                    search_query={
                        "include-deleted": request.args.get("include-deleted", "n"),
                        "role": int(request.args.get("role")) if request.args.get("role") else "",
                        "status": request.args.get("status"),
                        "name": request.args.get("name", ""),
                        "email": request.args.get("email", ""),
                        "sorting": request.args.get("sorting")})

    @shaft_deco.nav_title("User Info", visible=False)
    def info(self, id):
        page_meta("User Info")
        user = models.AuthUser.get(id, include_deleted=True)
        if not user:
            abort(404, "User doesn't exist")

        if current_user.role.level < user.role.level:
            abort(403, "Not enough rights to access this user info")

        return {
            "user": user,
            "user_roles_options": self._user_roles_options()
        }

    @shaft_deco.allow_post
    def action(self):
        id = request.form.get("id")
        action = request.form.get("action")

        try:
            user = models.AuthUser.get(id, include_deleted=True)

            if not user:
                abort(404, "User doesn't exist or has been deleted!")
            if current_user.role.level < user.role.level:
                abort(403, "Not enough power level to update this user info")

            if current_user.id != user.id:
                if action == "activate":
                    user.update(active=True)
                    flash_success("User has been ACTIVATED")
                elif action == "deactivate":
                    user.update(active=False)
                    flash_success("User is now DEACTIVATED")
                elif action == "delete":
                    user.delete()
                    flash_success("User has been DELETED")
                elif action == "undelete":
                    user.delete(False)
                    flash_success("User is now RESTORED")

            if action == "info":
                name = request.form.get("name")
                if not name:
                    abort(400, "Missing Name")
                data = {
                    "name": request.form.get("name"),
                }

                if current_user.id != user.id:
                    user_role = request.form.get("user_role")
                    _role = models.AuthRole.get(user_role)
                    if not _role:
                        raise exceptions.AuthError("Invalid ROLE selected")
                    data["role"] = _role

                user.update(**data)
                flash_success("User info updated successfully!")

            elif action == "change-email":
                user_login = user.get_login()
                if not user_login:
                    raise exceptions.AuthError("This account doesn't have an email login type")
                email = request.form.get("email")
                if email != user_login.email:
                    user_login.change_email(email)
                    flash_success("Email '%s' updated successfully!" % email)

            elif action == "change-password":
                user_login = user.get_login()
                if not user_login:
                    raise exceptions.AuthError("This account doesn't have an email login type")
                password = request.form.get("password", "").strip()
                password_confirm = request.form.get("password_confirm", "").strip()
                change_password(user, password, password_confirm)
                flash_success("Password changed successfully!")

            elif action == "email-reset-password":
                send_password_reset_email(user=user)
                flash_success("Password reset was sent to email")

            elif action == "email-account-verification":
                send_email_verification_email(user)
                flash_success("Email verification was sent")

            elif action == "reset-secret-key":
                user.reset_secret_key()
                flash_success("The account's secret key has been changed")

            elif action == "delete-profile-image":
                profile_image_object_name = user.profile_image.get("object_name")
                if profile_image_object_name:
                    obj = storage.get(profile_image_object_name)
                    if obj is not None:
                        obj.delete()
                        user.update_profile_image(url=None, object_name=None)


                flash_success("Profile Image deleted successfully!")

        except exceptions.AuthError as ae:
            flash_error(ae.message)
        return redirect(self.info, id=id)


    @shaft_deco.allow_post
    def create(self):
        try:

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            password_confirm = request.form.get("password_confirm", "").strip()

            user_role = request.form.get("user_role")
            role = models.AuthRole.get(user_role)
            if not role:
                raise exceptions.AuthError("Invalid ROLE selected")
            if not name:
                raise shaft_exc.AppError("Name is required")
            elif not password or password != password_confirm:
                raise shaft_exc.AppError("Passwords don't match")

            user = register(email=email,
                             password=password,
                             name=name,
                             role_name=role.name)

            if user:
                flash_success("New account created successfully!")
                return redirect(self.info, id=user.id)
            else:
                raise exceptions.AuthError("Account couldn't be created")
        except exceptions.AuthError as ae:
            flash_error(ae.message)

        return redirect(self.index)

    @shaft_deco.nav_title("User Roles", order=2)
    @shaft_deco.allow_post_get
    def roles(self):
        """
        Only admin and super admin can add/remove roles
        RESTRICTED ROLES CAN'T BE CHANGED
        """
        roles_max_range = 11
        if request.method == "POST":
            try:
                id = request.form.get("id")
                name = request.form.get("name")
                level = request.form.get("level")
                action = request.form.get("action")
                if name and level:
                    level = int(level)
                    name = name.upper()
                    _levels = [r[0] for r in models.AuthRole.ROLES]
                    _names = [r[1] for r in models.AuthRole.ROLES]
                    if level in _levels or name in _names:
                        raise exceptions.AuthError("Can't modify PRIMARY Roles - name: %s, level: %s " % (name, level))
                    else:
                        if id:
                            role = models.AuthRole.get(id)
                            if role:
                                if action == "delete":
                                    role.update(level=0)  # Free the role
                                    role.delete()
                                    flash_success("Role '%s' deleted successfully!" % role.name)
                                elif action == "update":
                                    if role.level != level and models.AuthRole.get_by_level(level):
                                        raise exceptions.AuthError("Role Level '%s' exists already" % level)
                                    elif role.name != models.AuthRole.slug_name(name) and models.AuthRole.get_by_name(name):
                                        raise exceptions.AuthError("Role Name '%s'  exists already" % name)
                                    else:
                                        role.update(name=name, level=level)
                                        flash_success("Role '%s (%s)' updated successfully" % (name, level))
                            else:
                                raise exceptions.AuthError("Role doesn't exist")
                        else:
                            if models.AuthRole.get_by_level(level):
                                raise exceptions.AuthError("New Role Level '%s' exists already" % level)
                            elif models.AuthRole.get_by_name(name):
                                raise exceptions.AuthError( "New Role Name '%s'  exists already" % name)
                            else:
                                models.AuthRole.new(name=name, level=level)
                                flash_success("New Role '%s (%s)' addedd successfully" % (name, level))
            except exceptions.AuthError as ex:
                flash_error("%s" % ex.message)
            return redirect(self.roles)

        page_meta("User Roles")
        roles = models.AuthRole.query().order_by(models.AuthRole.level.desc())

        allocated_levels = [r.level for r in roles]
        #levels_options = [(l, l) for l in range(1, roles_max_range) if l not in allocated_levels]
        levels_options = [(l, l) for l in range(1, roles_max_range)]

        return {
                "roles": roles,
                "levels_options": levels_options
                }


