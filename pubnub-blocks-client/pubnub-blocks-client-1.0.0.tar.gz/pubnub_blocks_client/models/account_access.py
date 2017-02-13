"""PubNub REST API access information model."""
from pubnub_blocks_client.models.model import MutableModel


class AccountAccess(MutableModel):
    """PubNub account access information model."""

    def __init__(self, email, password):
        """Construct account access information object.

        Construct object which is used to access PubNub REST API on user's
        behalf.
        :type email:     str
        :param email:    User's email address which has been used during
                         account registration on https://admin.pubnub.com
        :type password:  str
        :param password: Password which has been chosen during account.
        """
        data = dict(email=email, password=password)
        super(AccountAccess, self).__init__(data)

    @property
    def email(self):
        """Stores reference on user's email address.

        :rtype:  str
        :return: Reference on user's email address.
        """
        return self.get_property('email')

    @property
    def password(self):
        """Stores reference on password from user account.

        :rtype:  str
        :return: Reference on password for account.
        """
        return self.get_property('password')

    @property
    def token(self):
        """Stores reference on account access token.

        :rtype:  str
        :return: Reference on received account access token.
        """
        return self.get_property('token')

    @token.setter
    def token(self, value):
        """Update account access token.

        :type value:  str
        :param value: Reference on new account access token which should be
                      be used with PubNub REST API.
        """
        self.set_property('token', value, original=True)

    @property
    def is_valid(self):
        """Stores whether access model is valid or not.

        Valid access model should contain email/password and/or token. If
        token is missing and one of email or password is missing - this is
        invalid access model.
        """
        return self.has_credentials or self.token

    @property
    def has_credentials(self):
        """Stores whether required authorization credentials has been
        provided.

        :rtype:  bool
        :return: 'True' in case if both email and password has been
                 provided.
        """
        return self.email and self.password

    def restore(self, cache):
        """Restore account access information from passed cache.

        Re-initialize account access model using data which has been
        exported from account during last module usage. Passed cache should
        be in exact format as it has been exported.
        :type cache:  dict
        :param cache: Reference on dictionary which contain account access
                      model information.
        """
        self.update(cache)

    def missing_credentials(self):
        """Retrieve list of credentials which is missing.

        :rtype:  list[str]
        :return: List of credential names.
        """
        credentials = list()
        if not self.email:
            credentials.append('email')
        if not self.password:
            credentials.append('password')

        return credentials
