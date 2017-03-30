"""PubNub REST API access information model."""
from pubnub_blocks_client.exceptions import GeneralPubNubError, AccountError
from pubnub_blocks_client.models.model import MutableModel
import pubnub_blocks_client.core.api as api


class APIAccess(MutableModel):
    """PubNub REST API access information model."""

    def __init__(self, email=None, password=None):
        """Construct REST API access information model.

        Construct object which is used to access PubNub REST API on user's
        behalf.
        :type email:     str | None
        :param email:    User's email address which has been used during
                         account registration on https://admin.pubnub.com
        :type password:  str | None
        :param password: Password which has been chosen during registration.
        """
        data = dict(email=email, password=password)
        super(APIAccess, self).__init__(data)

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
        :return: Reference on password for user account.
        """
        return self.get_property('password')

    @property
    def _token(self):
        """Stores reference on user access token.

        :rtype:  str
        :return: Reference on received user access token.
        """
        return self.get_property('token')

    @_token.setter
    def _token(self, value):
        """Update user access token.

        :type value:  str
        :param value: Reference on new user access token which should be be
                      used with PubNub REST API.
        """
        self.set_property('token', value, original=True)

    @property
    def _is_valid(self):
        """Stores whether access model is valid or not.

        Valid access model should contain email/password and/or token. If
        token is missing and one of email or password is missing - this is
        invalid access model.
        """
        return self.has_credentials or self._token is not None

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
        """Restore user access information from passed cache.

        Re-initialize user access model using data which has been exported
        during last module usage. Passed cache should be in exact format as
        it has been exported.

        WARNING: This method should be used internally by module itself.

        :type cache:  dict
        :param cache: Reference on dictionary which contain user access
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

    def token(self, expired=False):
        """Retrieve reference on REST API access token.

        Previously stored token information will be returned or new request
        will be done. If token marked as expired, new token value will be
        requested.

        :raise: AuthorizationError in case if not all or wrong credentials
                has been provided. GeneralPubNubError will be raised in
                case if occurred error which is not related to
                authorization request.
        :raise: GeneralPubNubError in case of network issues or response
                parsing error.

        :type expired:  bool
        :param expired: Whether token should be treated as expired or not
                        (in case if REST API call with it returned 403
                        status code).

        :rtype:  str
        :return: REST API access token.
        """
        if self._token is None or expired:
            if not self.has_credentials:
                credentials = self.missing_credentials()
                raise AccountError.missing_credentials(credentials)

            # Authorize user and process response.
            result, error = api.authorize(email=self.email,
                                          password=self.password)

            # Check whether authorization has been successful or not.
            if error is not None:
                if error['code'] == 400:
                    raise AccountError.wrong_credentials(error['error'])
                else:
                    raise GeneralPubNubError(error['error'])

            self._token = result.get('token')

        return self._token
