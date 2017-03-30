"""PubNub user representation module."""
from pubnub_blocks_client.exceptions import GeneralPubNubError, AccountError
import pubnub_blocks_client.models.api_access as api_access
from pubnub_blocks_client.models.account import Account
from pubnub_blocks_client.models.model import MutableModel
import pubnub_blocks_client.core.api as api


class User(MutableModel):
    """PubNub user representation module."""

    def __init__(self, email=None, password=None):
        """User model constructor.

        Construct and prepare user model for further usage with PubNub API.
        :type email:     str | None
        :param email:    User's email address which has been used during
                         PubNub user registration on
                         https://admin.pubnub.com

        :type password:  str | None
        :param password: Password which has been chosen during
                         registration.

        :rtype:  User
        :return: Initialized user's data model.
        """
        additional_fields = ['pnm_accounts', 'pnm_access']
        super(User, self).__init__(additional_fields=additional_fields)
        self._access = api_access.APIAccess(email=email, password=password)
        self._accounts = None
        """:type: list[Account]"""

    def _get_non_property(self, name):
        """Retrieve one of pre-processed values.

        :type name:  str
        :param name: Reference on name of custom fields for which
                     serialized data should be provided by instance.

        :rtype:  list | dict
        :return: Requested serialized data.
        """
        if name == 'pnm_accounts':
            return list(dict(acc) for acc in self._accounts or list())
        elif name == 'pnm_access':
            return dict(self._access) if self._access is not None else dict()

    @property
    def access(self):
        """Stores reference on REST API access information object.

        :rtype:  APIAccess
        :return: REST API access information object.
        """
        self._fetch_user_profile_if_required()

        return self._access

    @property
    def uid(self):
        """Stores reference on unique PubNub user identifier.

        :rtype:  int
        :return: Reference on unique PubNub user identifier.
        """
        self._fetch_user_profile_if_required()

        return self.get_property('user.id', is_path=True)

    @property
    def creation_date(self):
        """Stores reference on PubNub user creation date.

        Date stored in unix-timestamp format.
        :rtype:  int
        :return: Reference on PubNub user registration date.
        """
        self._fetch_user_profile_if_required()

        return self.get_property('user.created', is_path=True)

    @property
    def first_name(self):
        """Stores reference on PubNub user first name

        :rtype:  str | None
        :return: Reference on PubNub user first name. 'None' in case if
                 value not provided.
        """
        self._fetch_user_profile_if_required()

        return self.get_property('user.properties.first', is_path=True)

    @property
    def last_name(self):
        """Stores reference on PubNub user last name

        :rtype:  str | None
        :return: Reference on PubNub user last name. 'None' in case if
                 value not provided.
        """
        self._fetch_user_profile_if_required()

        return self.get_property('user.properties.last', is_path=True)

    @property
    def phone(self):
        """Stores reference on account owner first name

        :rtype:  int
        :return: Reference on account owner contact number.
        """
        self._fetch_user_profile_if_required()

        return self.get_property('user.properties.phone', is_path=True)

    @property
    def email(self):
        """Stores reference on account owner first name

        :rtype:  str
        :return: Reference on account owner contact email.
        """
        self._fetch_user_profile_if_required()

        return self.get_property('user.email', is_path=True)

    def accounts(self):
        """Retrieve list of accounts to which user has access.

        It is possible to share access to account with other users. When
        returned, first account in the list is owned by this user.

        :rtype:  list[Account]
        :return: Reference on list of account models.
        """
        if self._accounts is None:
            results = self._fetch_accounts()

            # Update list of accounts to which user has access.
            self._accounts = list()
            for account_data in results.get('accounts'):
                # Construct account model from received data.
                acc = Account(data=account_data, access=self._access,
                              backward_compatibility=False)
                self._accounts.append(acc)

        return self._accounts

    def account(self, name=None, uid=None):
        """Retrieve reference on specific account by it's name or uid.

        :type name:  str | None
        :param name: Name of account which should be returned (based on
                     company name)
        :type uid:   int | None
        :param uid:  Unique identifier which has been assigned to account.

        :rtype:  Account | None
        :return: Reference on requested account model or 'None' in case if
                 there is no model with specified identifiers.
        """
        target_account = None
        for account in self.accounts():
            if name is not None and account.name == name or \
               uid is not None and account.uid == uid:
                target_account = account
                break

        return target_account

    def restore(self, cache):
        """Restore user information from passed cache.

        Re-initialize user model using data which has been exported from
        during last module usage. Passed cache should be in exact format as
        it has been exported.
        :type cache:  dict
        :param cache: Reference on dictionary which contain full or partial
                      user state information.
        """
        if cache:
            if 'pnm_access' in cache:
                self._access = api_access.APIAccess()
                self._access.restore(cache.pop('pnm_access'))
            if 'pnm_accounts' in cache:
                self._accounts = list()
                acc = cache.pop('pnm_accounts')
                for account_data in acc:
                    acc = Account()
                    acc.restore(account_data, access=self._access)
                    self._accounts.append(acc)
            self.update(cache)

    def save(self):
        """Store any changes to user and related data structures.

        If user or any related to current module run component has been
        changed it should be saved using REST API.
        """
        for acc in self.accounts():
            acc.save()

    def _fetch_accounts(self):
        """Perform call to REST API which will return list of accounts.

        Fetch JSON object which contain list of accounts to which
        authorized user has access.

        :rtype:  dict
        :return: Reference on dictionary which contain list of accounts
                 along with access permissions which has been provided
                 when account has been shared with authorized user.
        """
        self._fetch_user_profile_if_required()

        result = None
        if self._accounts is None:
            result, error = api.accounts(access=self._access, user_id=self.uid)

            # Handle accounts list fetch (if request did fail).
            self._handle_error_if_required(error)

        return result

    def _fetch_user_profile_if_required(self):
        """Retrieve PubNub user profile if not received it earlier.

        :raise: AuthorizationError in case if not all or wrong credentials
                has been provided. GeneralPubNubError will be raised in
                case if occurred error which is not related to
                authorization request.
        :raise: GeneralPubNubError in case of network issues or response
                parsing error.
        """
        if self.is_empty:
            # PubNub BLOCKS can't be used without proper authorization
            # credentials.
            if not self._access.has_credentials:
                credentials = self._access.missing_credentials()
                raise AccountError.missing_credentials(credentials)

            result, error = api.authorize(email=self._access.email,
                                          password=self._access.password)

            # Handle user authorization error (if request did fail).
            self._handle_error_if_required(error)

            # Update REST API access token (to not perform second request
            # from APIAccess model when token will be requested.
            if result.get('token') is not None:
                self._access.update(dict(token=result.pop('token')))

            self.update(result)

    @staticmethod
    def _handle_error_if_required(error):
        """Process request error if passed.

        :raise: AuthorizationError in case if not all or wrong credentials
                has been provided. GeneralPubNubError will be raised in
                case if occurred error which is not related to
                authorization request.
        :raise: GeneralPubNubError in case of network issues or response
                parsing error.

        :type error:  dict
        :param error: Reference on dictionary which describe error reason
                      and origin.
        """
        if error:
            if error['code'] == 401:
                raise AccountError.insufficient_rights(error.get('error'))
            else:
                raise GeneralPubNubError(error['error'])
