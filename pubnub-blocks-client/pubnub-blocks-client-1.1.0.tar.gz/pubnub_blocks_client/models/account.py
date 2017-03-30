"""User account representation model."""
import copy
import pubnub_blocks_client.core.api as api
from pubnub_blocks_client.exceptions import GeneralPubNubError, AccountError
from pubnub_blocks_client.models.application import Application
from pubnub_blocks_client.models.api_access import APIAccess
from pubnub_blocks_client.utils import value_for_key
from pubnub_blocks_client.models.owner import Owner
from pubnub_blocks_client.models.model import Model
import pubnub_blocks_client.utils as pn_utils


class Account(Model):
    """PubNub account representation model."""

    def __init__(self, *args, **kwargs):
        """Construct user account model.

        Model used to get access to all information which is available for
        user on PubNub admin portal. Additional data will be fetched
        on-demand.
        :type data:      dict | None
        :param data:     Service-provided account information.
        :type access:    APIAccess
        :param access:   Reference on REST API access information object.
        :type email:     str | None
        :param email:    User's email address which has been used during
                         account registration on https://admin.pubnub.com
                         [DEPRECATED]
        :type password:  str | None
        :param password: Password which has been chosen during account.
                         [DEPRECATED]

        :rtype:  Account
        :return: Initialized user's account data model.
        """
        additional_fields = ['pnm_applications']
        if kwargs.get('access') is None:
            additional_fields.extend(['pnm_access', 'pnm_owner'])
        super(Account, self).__init__(additional_fields=additional_fields)

        # Notify about deprecated parameters in case if class used in
        # backward compatibility mode.
        self._backward_compatibility = kwargs.get('access') is None
        Account._report_deprecated_parameters(self._backward_compatibility)

        # Update variable key/value parameter with data received using
        # backward compatibility.
        if self._backward_compatibility:
            email, password = Account._auth_credentials(*args, **kwargs)
            self._access = APIAccess(email=email, password=password)
            self._user_id = None
        else:
            self._access = kwargs.get('access')
            """:type : APIAccess"""
            # Update account model data.
            self.update(kwargs.get('data'))

        self._owner = None
        """:type : Owner"""
        self._apps = None
        """:type : dict"""

    def _get_non_property(self, name):
        """Retrieve one of pre-processed values.

        :type name:  str
        :param name: Reference on name of custom fields for which
                     serialized data should be provided by instance.

        :rtype:  list | dict
        :return: Requested serialized data.
        """
        if name == 'pnm_access':
            return dict(self._access) if self._access is not None else dict()
        elif name == 'pnm_owner':
            return dict(self._owner) if self._owner is not None else dict()
        else:
            return list(dict(app) for app in self.applications or list())

    @property
    def uid(self):
        """Stores reference on unique PubNub account identifier.

        :rtype:  int
        :return: Unique PubNub account identifier.
        """
        return self.get_property('id')

    @property
    def owner(self):
        """Stores reference on account owner model.

        :rtype:  Owner | None
        :return: Reference on initialized account owner model. 'None'
                 returned in case if account not authorized.
        """
        pn_utils.scan_environment_for_ansible()
        if not pn_utils.RUNNING_AS_ANSIBLE_MODULE:
            import warnings
            warnings.simplefilter("always")
            warnings.warn('Account \'owner\' property has been deprecated. '
                          'Account owner information described by user which '
                          'has access to account or if user different from '
                          'account owner it can be received from \'owner_id\'',
                          DeprecationWarning)

        if self._backward_compatibility:
            # Complete account initialization if required.
            self._initialize_if_required()

        return self._owner

    # noinspection PyDeprecation
    @owner.setter
    def owner(self, value):
        """Update account owner model.
        WARNING: This method should be used internally by module itself.
        :type value:  Owner
        :param value: Reference on account's owner data model.
        """
        self._owner = value

    @property
    def owner_id(self):
        """Stores reference on unique PubNub account owner user identifier.

        :rtype:  int
        :return: Unique PubNub account owner user identifier.
        """
        return self.get_property('owner_id')

    @property
    def name(self):
        """Stores reference on account name (based on company name).

        :rtype:  str
        :return: Account name.
        """
        return self.get_property('properties.company', is_path=True)

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

    def application_exists(self, name=None, uid=None):
        """Check whether specific applications registered for account or
        not.

        :type name:  str | None
        :param name: Reference on application name for which existence
                     should be checked.
        :type uid:   int | None
        :param uid:  Reference on unique application identifier for which
                     existence should be checked.

        :rtype:  bool
        :return: 'True' in case if specified application registered for
                 account.
        """
        # Make sure what account data model fully initialized.
        self._fetch_applications_if_required()

        exists = False
        if name:
            exists = name in self._apps
        elif uid is not None:
            for app in self.applications:
                if app.uid == uid:
                    exists = True
                    break

        return exists

    def application(self, name=None, uid=None):
        """Retrieve reference on specific application which is registered
        for account.

        :type name:  str | None
        :param name: Reference on application name for which model should
                     be retrieved from list of registered applications.
        :type uid:   int | None
        :param uid:  Reference on unique application identifier for which
                     model should be retrieved from list of registered
                     applications.

        :rtype:  Application
        :return: Reference on one of registered applications.
        """
        # Make sure what account data model fully initialized.
        self._fetch_applications_if_required()

        application = value_for_key(self._apps, name)
        if application is None and uid is not None:
            for app in self.applications:
                if app.uid == uid:
                    application = app
                    break

        return application

    def restore(self, cache, access=None):
        """Restore account information from passed cache.

        Re-initialize user account model using data which has been exported
        from account during last module usage. Passed cache should be in
        exact format as it has been exported.
        :type cache:    dict
        :param cache:   Reference on dictionary which contain full or
                        partial user account state information.
        :type access:   APIAccess | None
        :param access:  Reference on REST API access information object.
        """
        if cache:
            apps = list()
            if access is not None:
                self._access = access
            if 'pnm_access' in cache:
                self._access.restore(cache.pop('pnm_access'))
            if 'pnm_owner' in cache:
                self._owner = Owner(cache.pop('pnm_owner'))
            if 'pnm_applications' in cache:
                apps = cache.pop('pnm_applications')
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
        # Update account information if required.
        if account is not None:
            if 'token' in account:
                self._access.update(dict(token=account.get('token')))
                if self._owner is None:
                    self._owner = Owner(account)
                    self._user_id = self._owner.uid
            elif 'owner_id' in account:
                self.update(account)

        # Create models from list of account's applications.
        if applications is not None:
            if self._apps is None:
                self._apps = dict()
            for app in applications:
                application = Application(application=copy.deepcopy(app),
                                          access=self._access, initial=initial)
                self._apps[application.name] = application

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
            # Complete account initialization if required.
            self._initialize_if_required()

            # Requests applications for user account.
            result, error = api.account(access=self._access,
                                        account_id=self.uid)

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
            elif error['code'] == 401:
                raise AccountError.insufficient_rights(error.get('error'))
            else:
                raise GeneralPubNubError(error['error'])

    @classmethod
    def _report_deprecated_parameters(cls, backward_compatibility):
        """Notify about parameters deprecation.

        In case if Account module has been used in backward compatibility
        mode notify about their deprecation.
        :type backward_compatibility:  bool
        :param backward_compatibility: Whether backward compatibility
                                       enabled or not.
        """
        if backward_compatibility:
            pn_utils.scan_environment_for_ansible()
            if not pn_utils.RUNNING_AS_ANSIBLE_MODULE:
                import warnings
                warnings.simplefilter("always")
                warnings.warn('\'email\' and \'password\' parameters '
                              'deprecated starting from 1.1.0. Use User model'
                              ' to get access to it\'s accounts and '
                              'applications.',
                              DeprecationWarning)

    @classmethod
    def _auth_credentials(cls, *args, **kwargs):
        """Extract authorization credentials from provided parameters.

        This method used during backward compatibility to extract values
        which is passed to Account instance to be used as user authorization.

        :rtype:  list[str]
        :return: Reference on tuple which contain email and user password.
        """
        credentials = [None, None]
        if len(args):
            credentials.append(args[0])
            if len(args) > 1:
                credentials.append(args[1])
        if kwargs.get('email'):
            credentials[0] = kwargs.pop('email')
        if kwargs.get('password'):
            credentials[1] = kwargs.pop('password')

        return credentials

    ##########################################
    # BACKWARD COMPATIBILITY SUPPORT METHODS #
    ##########################################

    def _initialize_if_required(self):
        """Complete account initialization if required.

        During initialization process authorization request will be
        followed by accounts list fetch for authorized user.
        :raise: AuthorizationError in case if not all or wrong credentials
                has been provided. GeneralPubNubError will be raised in
                case if occurred error which is not related to
                authorization request.
        :raise: GeneralPubNubError in case of network issues or response
                parsing error.
        """
        if self._backward_compatibility:
            self._fetch_user_profile_if_required()
            self._fetch_accounts_if_required()

    def _fetch_user_profile_if_required(self):
        """Retrieve PubNub user profile if not received it earlier.

        :raise: AuthorizationError in case if not all or wrong credentials
                has been provided. GeneralPubNubError will be raised in
                case if occurred error which is not related to
                authorization request.
        :raise: GeneralPubNubError in case of network issues or response
                parsing error.
        """
        if self._owner is None:
            # PubNub BLOCKS can't be used without proper authorization
            # credentials.
            if not self._access.has_credentials:
                credentials = self._access.missing_credentials()
                raise AccountError.missing_credentials(credentials)

            result, error = api.authorize(email=self._access.email,
                                          password=self._access.password)
            # Handle user authorization error (if request did fail).
            self._handle_request_error(error)

            self._process_data(account=result)

    def _fetch_accounts_if_required(self):
        """Perform call to REST API which will return list of accounts.

        Fetch JSON object which contain list of accounts to which
        authorized user has access.
        """
        if self.uid is None:
            result, error = api.accounts(access=self._access,
                                         user_id=self._user_id)

            # Handle accounts list fetch (if request did fail).
            self._handle_request_error(error)

            # Retrieve reference on owner's account
            acc = result['accounts'][0]
            self._process_data(account=acc)
