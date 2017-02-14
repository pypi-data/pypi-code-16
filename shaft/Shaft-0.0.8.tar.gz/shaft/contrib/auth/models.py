
import datetime
import arrow
from . import exceptions
from flask_login import UserMixin
from shaft import (db,
                   utils,
                   send_mail,
                   _)
from shaft.exceptions import ModelError


class AuthRole(db.Model):

    SUPERADMIN = "SUPERADMIN"  # ALL MIGHTY, RESERVED FOR SYS ADMIN
    ADMIN = "ADMIN"  # App/Site admin
    MANAGER = "MANAGER"  # Limited access, but can approve EDITOR Data
    EDITOR = "EDITOR"  # Rights to write, manage, publish own data
    CONTRIBUTOR = "CONTRIBUTOR"  # Rights to only write and read own data
    MODERATOR = "MODERATOR"   # Moderate content
    MEMBER = "MEMBER"  # Just a member

    # BASIC ROLES
    ROLES = [(99, SUPERADMIN),
               (89, ADMIN),
               (59, MANAGER),
               (49, EDITOR),
               (39, CONTRIBUTOR),
               (29, MODERATOR),
               (10, MEMBER)]

    name = db.Column(db.String(75), index=True)
    level = db.Column(db.Integer, index=True)

    @classmethod
    def _syncdb(cls):
        """
        Shaft specific
        To setup some models data after
        :return:
        """
        [cls.new(level=r[0], name=r[1]) for r in cls.ROLES]

    @classmethod
    def new(cls, name, level):
        name = cls.slug_name(name)
        if not cls.get_by_name(name) and not cls.get_by_level(level):
            return cls.create(name=name, level=level)

    @classmethod
    def get_by_name(cls, name):
        name = cls.slug_name(name)
        return cls.query().filter(cls.name == name).first()

    @classmethod
    def get_by_level(cls, level):
        return cls.query().filter(cls.level == level).first()

    @classmethod
    def slug_name(cls, name):
        return utils.slugify(name)

class AuthUser(db.Model, UserMixin):
    role_id = db.Column(db.Integer, db.ForeignKey(AuthRole.id))
    name = db.Column(db.String(255))
    profile_image = db.Column(db.JSONType)
    contact_email = db.Column(db.String(75), index=True)
    registration_method = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True, index=True)
    last_login = db.Column(db.DateTime)
    last_visited = db.Column(db.DateTime)
    locale = db.Column(db.String(10), default="en")

    # A secret key to sign data per user. If a key is compromised,
    # we can reset this one only and not affect everyone else
    secret_key = db.Column(db.String(250))

    # Relationship to role
    role = db.relationship(AuthRole)


    # ------ FLASK-LOGIN REQUIRED METHODS ----------------------------------
    @property
    def is_active(self):
        return self.active

    # ---------- END FLASK-LOGIN REQUIREMENTS ------------------------------

    @classmethod
    def search_by_name(cls, query, name):
        query = query.filter(db.or_(cls.name.contains(name)))
        return query

    @property
    def email(self):
        return self.login_email

    @property
    def login_email(self):
        user_login = self.get_login("email")
        return user_login.email if user_login else None

    @property
    def login_email_verfied(self):
        user_login = self.get_login("email")
        return True if user_login and user_login.email_verified else False

    @property
    def profile_image_url(self):
        return self.profile_image.get("url")

    def update_profile_image(self, url, object_name, **kwargs):
        """Update the profile image """
        kwargs.update({
            "url": url,
            "object_name": object_name
        })
        self.update(profile_image=kwargs)

    def has_any_roles(self, *roles):
        """
        Check if user has any of the roles requested
        :param roles: tuple of roles string
        :return: bool
        """
        roles = map(utils.slugify, list(roles))

        return True \
            if AuthRole.query()\
            .join(AuthUser)\
            .filter(AuthRole.name.in_(roles))\
            .filter(AuthUser.id == self.id)\
            .count() \
            else False

    def get_login(self, provider="email", social_name=None):
        """
        Return the UserLogin by type
        :param provider: the type of login: email, username
        :param social_name: if type is SOCIAL, it requires the social name, ie: facebook
        :return: AuthUserLogin
        """

        login = self.logins.filter(AuthUserLogin.provider == provider)
        if social_name:
            login = login.filter(AuthUserLogin.social_provider == social_name)
        return login.first()

    def has_login_type(self, provider):
        return True if self.get_login(provider) else False

    def send_email(self, template, **kwargs):
        """
        To send mail to user's .
        Usually for communication purposes
        :param template:
        :param kwargs: custom data to pass
        :return:
        """
        return send_mail(template=template,
                         to=self.contact_email,
                         user=self.email_data,
                         **kwargs)

    @property
    def email_data(self):
        """
        Return some basic user info for email
        :return:
        """
        return {
            "id": self.id,
            "name": self.name,
            "contact_email": self.contact_email
        }

    def set_role(self, role):
        role_ = AuthRole.get_by_name(role.upper())
        if not role_:
            raise ModelError("Invalid user role: '%s'" % role)
        self.update(role=role_)

    def reset_secret_key(self):
        """
        Run this whenever there is a security change in the account.
        ie: password change.
        BTW, AuthUserLogin.change_password, already performs this method
        """
        self.update(secret_key=utils.guid())

    @property
    def secret_salt(self):
        return "USER:%s" % self.id

    def sign_data(self, data, expires_in=None, url_safe=True):
        """
        To safely sign a user data
        :param data: mixed
        :param expires_in: The time for it to expire
        :param url_safe: bool. If true it will allow it to be passed in URL
        :return: str -  the token/signed data
        """
        if url_safe:
            return utils.sign_url_safe(data,
                                       secret_key=self.secret_key,
                                       salt=self.secret_salt,
                                       expires_in=expires_in)
        else:
            return utils.sign_data(data,
                                   secret_key=self.secret_key,
                                   salt=self.secret_salt,
                                   expires_in=expires_in)

    def unsign_data(self, data, url_safe=True):
        """
        Retrieve the signed data. If it is expired, it will throw an exception
        :param data: token/signed data
        :param url_safe: bool. If true it will allow it to be passed in URL
        :return: mixed, the data in its original form
        """
        if url_safe:
            return utils.unsign_url_safe(data,
                                         secret_key=self.secret_key,
                                         salt=self.secret_salt)
        else:
            return utils.unsign_data(data,
                                     secret_key=self.secret_key,
                                     salt=self.secret_salt)

    def signed_data_match(self, data, matched_data, url_safe=True):
        try:
            u_data = self.unsign_data(data, url_safe=url_safe)
            return u_data == matched_data
        except Exception as e:
            return False

class AuthUserLogin(db.Model):
    TYPE_EMAIL = "email"
    TYPE_SOCIAL = "social"
    PROVIDER_FACEBOOK = "facebook"
    PROVIDER_TWITTER = "twitter"
    PROVIDER_EMAIL = "email"

    user_id = db.Column(db.Integer, db.ForeignKey(AuthUser.id))
    provider = db.Column(db.String(50), index=True)
    email = db.Column(db.EmailType, index=True)
    username = db.Column(db.String(250), index=True)
    social_token = db.Column(db.JSONType)
    social_id = db.Column(db.String(255), index=True)
    email_verified = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255))
    require_password_change = db.Column(db.Boolean, default=False)
    user = db.relationship(AuthUser, backref=db.backref('logins', lazy='dynamic'))

    @classmethod
    def encrypt_password(cls, password):
        return utils.encrypt_string(password)

    @classmethod
    def new(cls,
            email=None,
            username=None,
            password=None,
            provider="email",
            name=None,
            social_token=None,
            social_id=None,
            random_password=True,
            role=None,
            user=None):


        if not user and not name:
            raise exceptions.AuthError(_("Missing User's name"))
        if email and not utils.is_email_valid(email):
            raise exceptions.AuthError(_("Invalid email"))
        if username and not utils.is_username_valid(email):
            raise exceptions.AuthError(_("Invalid username"))

        data = {"provider": provider}
        if email:
            data["email"] = email

        if provider.lower() in ["email", "username"]:
            if not password and random_password:
                password = utils.generate_random_string()
            if not utils.is_password_valid(password):
                raise exceptions.AuthError(_("Password is required"))
            data["password_hash"] = cls.encrypt_password(password)
            data["email_verified"] = False
            if email:
                if cls.get_by_email(email):
                    raise exceptions.AuthError(_("Email exists already"))
            if username:
                if cls.get_by_username(username):
                    raise exceptions.AuthError(_("Email exists already"))
                data["username"] = username
        elif social_token and social_id:
            data["social_id"] = social_id
            data["social_token"] = social_token
        else:
            raise exceptions.AuthError(_("Invalid provider"))

        if not user:
            if not role:
                role = AuthRole.get_by_name("MEMBER")
            if not role:
                raise exceptions.AuthError(_("Missing User's Role"))
            user = AuthUser(name=name,
                            registration_method=data["provider"].lower(),
                            active=True,
                            role=role)
        data["user"] = user
        login = cls.create(**data)
        login.user.reset_secret_key()
        return login


    @classmethod
    def get_by_email(cls, email):
        """
        Return a User by email address
        """
        return cls.query().filter(cls.email == email).first()

    @classmethod
    def get_by_username(cls, username):
        """
        Return a User by email address
        """
        return cls.query().filter(cls.username == username).first()

    @classmethod
    def get_by_social(cls, provider, social_id):
        return cls.query() \
            .filter(cls.provider == provider) \
            .filter(cls.social_id == social_id) \
            .first()

    @property
    def is_email(self):
        return self.provider.lower() == "email"

    @property
    def is_username(self):
        return self.provider.lower() == "username"

    @property
    def is_social(self):
        return self.provider.lower() not in ["email", "username"]

    @property
    def token(self):
        return self.social_token

    def set_email_verified(self, verified=False):
        self.update(email_verified=verified)

    def password_matched(self, password):
        """
        Check if the password matched the hash
        :returns bool:
        """
        return utils.verify_encrypted_string(password, self.password_hash)

    def change_email(self, email):
        """
        Change account email
        :param email:
        :return: the email provided
        """
        if self.provider != self.TYPE_EMAIL:
            raise ModelError("Invalid login type. Must be the type of email to change email")

        if not utils.is_email_valid(email):
            raise exceptions.AuthError("Email address invalid")
        if self.email != email:
            if self.get_by_email(email):
                raise exceptions.AuthError("Email exists already")
            self.update(email=email)
            return True
        return email

    def change_username(self):
        pass

    def change_password(self, password):
        """
        Change the password.
        :param password:
        :return:
        """
        if self.provider != self.TYPE_EMAIL:
            raise ModelError("Invalid login type. Must be the type of email to change password")
        if not utils.is_password_valid(password):
            raise exceptions.AuthError("Invalid password")
        self.update(password_hash=self.encrypt_password(password),
                    require_password_change=False)

        # Whenever the password is changed, reset the secret key to invalidate
        # any tokens in the wild
        self.user.reset_secret_key()

        return password


    @property
    def active(self):
        return self.user.active

