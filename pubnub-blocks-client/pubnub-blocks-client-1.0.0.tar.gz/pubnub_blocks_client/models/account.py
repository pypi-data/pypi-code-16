"""User account representation model."""
from pubnub_blocks_client.exceptions import GeneralPubNubError, AccountError
from pubnub_blocks_client.models.account_access import AccountAccess
from pubnub_blocks_client.models.application import Application
from pubnub_blocks_client.utils import value_for_key
from pubnub_blocks_client.models.owner import Owner
from pubnub_blocks_client.models.model import Model
import pubnub_blocks_client.core.api as api


class Account(Model):
    """PubNub account representation model."""

    def __init__(self, email=None, password=None):
        """Construct user account model.

        Model used to get access to all information which is available for
        user on PubNub admin portal. Additional data will be fetched
        on-demand.
        :type email:     str | None
        :param email:    User's email address which has been used during
                         account registration on https://admin.pubnub.com
        :type password:  str | None
        :param password: Password which has been chosen during account.

        :rtype:  Account
        :return: Initialized user's account data model.
        """
        additional_fields = ['pnm_applications', 'pnm_access']
        super(Account, self).__init__(additional_fields=additional_fields)
        self._access = AccountAccess(email=email, password=password)
        self._owner = None
        """:type : Owner"""
        self._apps = None
        """:type : dict"""

    def _get_non_property(self, name):
        """Retrieve one of pre-processed values.

        Depending from passed name access information or applications will
        be returned.
        :type name:  str
        :param name: Reference on one of: pnm_access or pnm_applications.

        :rtype:  list | dict
        :return: Serialized access information or registered applications.
        """
        if name == 'pnm_access':
            return dict(self._access)
        else:
            return list(dict(app) for app in self.applications)

    @property
    def owner(self):
        """Stores reference on account owner model.

        :rtype:  Owner | None
        :return: Reference on initialized account owner model. 'None'
                 returned in case if account not authorized.
        """
        # Make sure what account authorized.
        self._authorize_if_required()

        return self._owner

    @property
    def applications(self):
        """Stores reference on list of application models.

        All applications which is registered for this account represented
        by models and stored in this property.
        :rtype:  list[Application]
        :return: List of application models.
        """
        # Make sure what applications list has been received.
        self._fetch_applications_if_required()

        return list(self._apps.values())

    @property
    def will_change(self):
        """Stores whether some portion of account's data will be changed.

        :rtype:  bool
        :return: 'True' in case if account or applications will change
                 during save process.
        """
        will_change = False
        if not self.changed:
            for application in self.applications:
                will_change = application.will_change
                if will_change:
                    break

        return will_change

    @property
    def changed(self):
        """Stores whether something changed in account's data.

        Whether something has been changed in account or it's components
        during last save operation.
        NOTE: Value will be reset as soon as new modifications will be done
        and will be set to proper value only after save operation
        completion.
        :rtype:  bool
        :return: 'True' in case if account or application data has been
                 modified.
        """
        changed = False
        for application in self.applications:
            changed = application.changed
            if changed:
                break

        return changed

    def application_exists(self, name):
        """Check whether specific applications registered for account or
        not.

        :type name:  str
        :param name: Reference on application name for which existence
                     should be checked.

        :rtype:  bool
        :return: 'True' in case if specified application registered for
                 account.
        """
        # Make sure what account data model fully initialized.
        self._fetch_applications_if_required()

        return name is not None and name in self._apps

    def application(self, name):
        """Retrieve reference on specific application which is registered
        for account.

        :type name:  str
        :param name: Reference on application name for which model should
                     be retrieved from list of registered applications.

        :raises: AccountError in case if there is no application with
                 specified name.

        :rtype:  Application
        :return: Reference on one of registered applications.
        """
        # Make sure what account data model fully initialized.
        self._fetch_applications_if_required()

        return value_for_key(self._apps, name)

    def restore(self, cache):
        """Restore account information from passed cache.

        Re-initialize user account model using data which has been exported
        from account during last module usage. Passed cache should be in
        exact format as it has been exported.
        :type cache:  dict
        :param cache: Reference on dictionary which contain full or partial
                      user account state information.
        """
        if cache:
            apps = list()
            if 'pnm_applications' in cache:
                apps = cache.pop('pnm_applications')
            if 'pnm_access' in cache:
                self._access.restore(cache.pop('pnm_access'))
            self._process_data(account=cache, applications=apps)

    def save(self):
        """Store any changes to account and related data structures.

        If account or any related to current module run component has been
        changed it should be saved using REST API.
        """
        for application in self.applications:
            application.save()

    def _process_data(self, account=None, applications=None, initial=False):
        """Process service / cached data to configure account data model.

        Configure or restore account model from previous module run using
        exported data. Restore allow to speed up module execution, because
        some REST API calls is pretty slow.
        :type account:       dict | None
        :param account:      Reference on dictionary which contain
                             information for account data model
                             configuration.
        :type applications:  list | None
        :param applications: Reference on list of dictionaries which
                             describe every application
                             which is registered for authorized account.
        :type initial:       bool
        :param initial:      Whether applications list processed on account
                             initialization from the scratch (not from
                             cache).
        """
        # Store account information if passed.
        if account is not None:
            self.update(account)
            # Update access token information if required.
            if self._access.token is None:
                self._access.token = account.get('token')
            # Update owner information.
            if self._owner is None:
                self._owner = Owner(account)

        # Create models from list of account's applications.
        if applications is not None:
            if self._apps is None:
                self._apps = dict()
            for app in applications:
                application = Application(application=app, access=self._access,
                                          initial=initial)
                self._apps[application.name] = application

    def _authorize_if_required(self):
        """Authorize account if it is required.

        Authorization request will be sent only if account not authorized
        or access information invalidated.
        :raise: AuthorizationError in case if not all or wrong credentials
                has been provided. GeneralPubNubError will be raised in
                case if occurred error which is not related to
                authorization request.
        """
        if self._owner is None:
            # PubNub BLOCKS can't be used without proper authorization
            # credentials.
            if not self._access.has_credentials:
                credentials = self._access.missing_credentials()
                raise AccountError.missing_credentials(credentials)

            # Authorize user and process response.
            result, error = api.authorize(email=self._access.email,
                                          password=self._access.password)

            # Check whether authorization has been successful or not.
            self._handle_request_error(error)
            self._process_data(account=result)

    def _fetch_applications_if_required(self):
        """Retrieve applications list if required.

        Applications request will be sent only if model's apps list not
        initialized.
        :raise: AuthorizationError in case if not all or wrong credentials
                has been provided. GeneralPubNubError will be raised in
                case if occurred error which is not related to
                authorization request.
        """
        if self._apps is None:
            # Requests applications for user account.
            owner_id = self.owner.uid
            result, error = api.account(token=self._access.token,
                                        account_id=owner_id)

            # Check whether applications list has been successful or not.
            self._handle_request_error(error)
            self._process_data(applications=result, initial=True)

    @staticmethod
    def _handle_request_error(error):
        """Handler request processing error.

        :type error:  dict | None
        :param error: Reference on request processing error information.
        """
        if error:
            if error['code'] == 400:
                raise AccountError.wrong_credentials(error['error'])
            else:
                raise GeneralPubNubError(error['error'])
