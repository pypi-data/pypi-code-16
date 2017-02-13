"""Application representation model."""
from pubnub_blocks_client.models.keyset import Keyset
from pubnub_blocks_client.utils import value_for_key
from pubnub_blocks_client.models.model import Model


class Application(Model):
    """PubNub application representation model."""

    def __init__(self, application, access, initial=False):
        """Construct application model using service response.

        :type application:  dict
        :param application: PubNub service response with information about
                            particular application.
        :type access:       AccountAccess
        :param: access      Reference on account access information.
        :type initial:      bool
        :param initial:     Whether application created during account
                            initialization from the scratch (not from
                            cache).
        :rtype:  Application
        :return: Initialized application data model.
        """
        super(Application, self).__init__(additional_fields=['keys'])
        self._access = access
        self._keysets = dict()
        """:type : list[str:Keyset]"""
        self._process_data(application=application, initial=initial)

    def _get_non_property(self, name):
        """Retrieve list of serialized keysets.

        Retrieve pre-processed (serialized) list of keysets which is
        registered for application.
        :type name:  str
        :param name: Reference on name which represent keyset field.

        :return: Serialized keysets list.
        """
        return list(dict(keyset) for keyset in self.keysets)

    @property
    def name(self):
        """Stores reference on registered application name.

        :rtype:  str
        :return: Reference on application name. 'None' will be returned in
                 case if application model configuration not completed.
        """
        return self.get_property('name')

    @property
    def keysets(self):
        """Stores reference on list of keyset models.

        All keysets which is registered for this application represented by
        models and stored in
        this property.
        :rtype:  list[Keyset]
        :return: List of keyset models.
        """
        return list(self._keysets.values())

    @property
    def will_change(self):
        """Stores whether some portion of application's data will be
        changed.

        :rtype:  bool
        :return: 'True' in case if application or keysets data will change
                 during save process.
        """
        will_change = False
        if not self.changed:
            for keyset in self.keysets:
                will_change = keyset.will_change
                if will_change:
                    break

        return will_change

    @property
    def changed(self):
        """Stores whether application's data has been changed or not.

        Whether something has been changed in application or it's
        components during last save operation.
        NOTE: Value will be reset as soon as new modifications will be done
        and will be set to proper value only after save operation
        completion.
        :rtype:  bool
        :return: 'True' in case if application or keysets data has been
                 modified.
        """
        changed = False
        for keyset in self.keysets:
            changed = keyset.changed
            if changed:
                break

        return changed

    def keyset_exists(self, name):
        """Check whether specific keyset registered for application or not.

        :type name:  str
        :param name: Reference on keyset name for which existence should be
                     checked.

        :rtype:  bool
        :return: 'True' in case if specified keyset registered for
                 application.
        """
        return name is not None and name in self._keysets

    def keyset(self, name):
        """Retrieve reference on specific keyset which is created for
        receiver application.

        :type name:  str
        :param name: Reference on keyset name for which model should be
                     retrieved from list of application's keysets.

        :raises: AccountError in case if there is no application with
                 specified name.

        :rtype:  Keyset
        :return: Reference on one of application's keysets.
        """
        return value_for_key(self._keysets, name)

    def save(self):
        """Store any changes to application and/or keyset.

        If application or any related to current module run component has
        been changed it should be saved using REST API.
        """
        for keyset in self.keysets:
            keyset.save()

    def _process_data(self, application, initial=False):
        """Process service / cached data to configure application data
        model.

        Configure application model from previous module run using exported
        data or service response.
        :type application:  dict
        :param application: Reference on dictionary which describe
                            application which is registered for authorized
                            account.
        :type initial:      bool
        :param initial:     Whether application created during account
                            initialization from the scratch (not from
                            cache).
        """
        keysets = list()
        if 'keys' in application:
            keysets = application.pop('keys')
        self.update(application)

        for keyset_data in keysets:
            keyset = Keyset(keyset=keyset_data, access=self._access,
                            initial=initial)
            self._keysets[keyset.name] = keyset
