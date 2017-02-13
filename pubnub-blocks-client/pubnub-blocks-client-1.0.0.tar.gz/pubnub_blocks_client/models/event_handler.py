"""Event handler representation model."""
import random
from pubnub_blocks_client.exceptions import EventHandlerError
from pubnub_blocks_client.models.model import MutableModel
from pubnub_blocks_client.utils import value_for_key
from pubnub_blocks_client.utils import is_equal
import pubnub_blocks_client.core.api as api


class EventHandler(MutableModel):
    """PubNub event handler representation model."""

    def __init__(self, name=None, channels=None, event=None, code=None):
        """Construct block model using service response.

        :type name:      str
        :param name:     Reference on event handler's name
        :type channels:  str
        :param channels: Reference on event handler's trigger channel.
        :type event:     str
        :param event:    Reference on event handler's trigger event.
        :type code:      str
        :param code:     Reference on event handler's code.

        :rtype:  EventHandler
        :return: Initialized event handler model.
        """
        super(EventHandler, self).__init__()
        self._changed = False
        self._access = None
        """:type: AccountAccess"""
        self._block_id = -1
        self._keyset_id = -1
        self._should_delete = False
        if name or channels or event or code:
            self.name = name
            self.channels = channels
            self.event = event
            self.code = code

    @property
    def uid(self):
        """Stores reference on unique block's identifier.

        :rtype:  int | None
        :return: Reference on unique event handler identifier. '-1' will be
                 returned in case if event handler model configuration not
                 completed or this is new model.
        """
        return self.get_property('id', default=-1)

    @property
    def name(self):
        """Stores reference on event handler's name.

        :rtype:  str
        :return: Reference on event handler's name. 'None' will be returned
                 in case if event handler model configuration not
                 completed.
        """
        return self.get_property('name', original=False)

    @name.setter
    def name(self, name):
        """Update event handler's name.

        :type name:  str
        :param name: Reference on new event handler name.
        """
        self.set_property('name', value=name)

    @property
    def code(self):
        """Stores reference on event handler's code.

        :rtype:  str
        :return: Reference on event handler's code. 'None' will be returned
                 in case if event handler model configuration not
                 completed.
        """
        return self.get_property('code', original=False)

    @code.setter
    def code(self, code):
        """Update event handler's code.

        :type code:  str
        :param code: Reference on new event handler code.
        """
        self.set_property('code', value=code)

    @property
    def channels(self):
        """Stores reference on event handler's trigger channel.

        :rtype:  str
        :return: Reference on event handler's trigger channel. 'None' will
                 be returned in case if event handler model configuration
                 not completed.
        """
        return self.get_property('channels', original=False)

    @channels.setter
    def channels(self, channels):
        """Update event handler's trigger channel.

        :type channels:  str
        :param channels: Reference on new event handler trigger channel.
        """
        self.set_property('channels', value=channels)

    @property
    def event(self):
        """Stores reference on event handler's trigger event.

        :rtype:  str
        :return: Reference on event handler's trigger event. 'None' will
                 be returned in case if event handler model configuration
                 not completed.
        """
        return self.get_property('event', original=False)

    @event.setter
    def event(self, event):
        """Update event handler's trigger event.

        :type event:  str
        :param event: Reference on new event handler trigger event.
        """
        self.set_property('event', value=event)

    @property
    def change_require_block_stop(self):
        """Check whether further event handlers require block to be
        stopped.

        All properties expect handler's name require to stop block before
        changing anything in handler.
        :rtype:  bool
        :return: 'True' in case if base handler data should be changed and
                 block should stop.
        """
        should_stop = self.uid == -1 or self.should_delete
        if not should_stop and not self.should_delete:
            # Retrieve user-provided handler information.
            fields = ['code', 'channels', 'event']
            cur = [self.get_property(name) for name in fields]
            upd = [self.get_property(name, mutated=True) for name in fields]
            should_stop = not is_equal(cur, upd)

        return should_stop

    @property
    def should_delete(self):
        """Stores whether event handler should be removed during save
        operation or not.

        Block removal will happen at the same moment when block will be
        asked to 'save' changes.
        :rtype:  bool
        :return: Whether event handler should be removed.
        """
        return self._should_delete

    @property
    def _payload(self):
        """Stores reference on event handler data structured as it required
        by PubNub service.

        :rtype:  dict
        :return: Event handler information in format which is known to
                 PubNub service.
        """
        payload = dict()
        if not self.is_empty:
            payload.update(key_id=self._keyset_id, block_id=self._block_id,
                           name=self.name, channels=self.channels,
                           code=self.code, event=self.event,
                           type=self.get_property('type'),
                           output=self.get_property('output'),
                           log_level=self.get_property('log_level'))

        return payload

    @property
    def will_change(self):
        """Stores whether some portion of event handler's data will be
        changed.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if event handler data will change during
                 save process.
        """
        will_change = False
        if not self.changed:
            will_change = (self.should_delete or self._should_create() or
                           self._should_save())

        return will_change

    @property
    def changed(self):
        """Check whether event handler's data has been changed or not.

        Whether something has been changed in event handler during last
        save operation.
        NOTE: Value will be reset as soon as new modifications will be done
        and will be set to proper value only after save operation
        completion.
        :rtype:  bool
        :return: 'True' in case if event handler data has been modified.
        """
        return self._changed

    def update_event_handler(self, block_id, keyset_id, event_handler=None,
                             access=None):
        """Update event handler information.

        :type block_id:       int
        :param block_id:      Reference on unique identifier of block for
                              which event handler registered.
        :type keyset_id:      int
        :param keyset_id:     Reference on unique identifier of keyset for
                              which block with event handler registered.
        :type event_handler:  dict
        :param event_handler: PubNub service response with information
                              about particular event handler.
        :type access:         AccountAccess
        :param access:        Reference on account access information.

        :rtype:  EventHandler
        :return: Initialized event handler model.
        """
        if access:
            self._access = access
        self._block_id = block_id
        self._keyset_id = keyset_id
        if event_handler:
            self._process_data(event_handler)

    def delete(self):
        """Remove event handler from block."""
        self._should_delete = True

    def save(self):
        """Save event handler's changes.

        Depending on whether event handler existed before or not it may be
        created and updated if required.
        """
        will_change = self.will_change
        handler_data = self._payload
        # Create new event handler if required.
        if self._should_create():
            handler_data.update(self._create_event_handler(handler_data))
        elif self._should_save():
            handler_data = self._save_changes(handler_data)
        elif self.should_delete:
            self._delete_event_handler()

        if will_change:
            self._changed = True
            if not self.should_delete:
                self._process_data(handler_data)

    def _should_create(self):
        """Check whether event handler should be created or not.

        :rtype:  bool
        :return: 'True' in case if this is new event handler (doesn't have
                 unique identifier assigned by PubNub service).
        """
        return self.uid == -1

    def _should_save(self):
        """Check whether there is event handlers changes which should be
        saved.

        :rtype:  bool
        :return: 'True' in case if there is unsaved changes.
        """
        should_save = self._should_create()
        if not should_save:
            should_save = self.data_changed()

        return should_save

    def _create_event_handler(self, payload):
        """Create new event handler and register it with block.

        :type payload:  dict
        :param payload: Reference on event handler payload which will be
                        populated with service response (contain base
                        information about new event handler).

        :rtype:  dict
        :return: Updated event handler payload.
        """
        fields = ['name', 'channels', 'event', 'code']
        values = [self.get_property(name, original=False) for name in fields]
        (name, channels, event, code) = tuple(values)
        payload.update(self._default_handler_payload() or dict())
        if name and channels and event and code:
            params = dict(token=self._access.token, keyset_id=self._keyset_id,
                          payload=payload)
            response, error = api.create_event_handler(**params)
            if error is not None:
                description = value_for_key(error, 'message')
                params = dict(event_handler=self.name, description=description)
                raise EventHandlerError.event_handler_create_error(**params)
            payload.update(response or dict())
        else:
            missed_fields = list()
            if not name:
                missed_fields.append('name')
            if not channels:
                missed_fields.append('channels')
            if not code:
                missed_fields.append('code')
            if not event:
                missed_fields.append('event')
            params = dict(event_handler=self.name, fields=missed_fields)
            raise EventHandlerError.event_handler_missing_fields(**params)

        return payload

    def _save_changes(self, payload):
        """Send event handler modifications to PubNub BLOCKS.

        :type payload:  dict
        :param payload: Reference on payload for event handler with all
                        modifications.
        """
        params = dict(token=self._access.token, keyset_id=self._keyset_id,
                      handler_id=self.uid, payload=payload)
        _, error = api.update_event_handler(**params)
        if error is not None:
            description = value_for_key(error, 'message')
            params = dict(event_handler=self.name, description=description)
            raise EventHandlerError.event_handler_update_error(**params)

        payload = self.mutable_data()
        payload.update(self._payload or dict())

        return payload

    def _delete_event_handler(self):
        """Remove existing event handler from block."""
        _, error = api.delete_event_handler(self._access.token,
                                            keyset_id=self._keyset_id,
                                            handler_id=self.uid)
        if error is not None:
            description = value_for_key(error, 'message')
            params = dict(event_handler=self.name, description=description)
            raise EventHandlerError.event_handler_remove_error(**params)

    def _process_data(self, event_handler):
        """Process received event handler's information.

        Use provided information to complete event handler initialization.
        :type event_handler:  dict
        :param event_handler: Reference on dictionary with event handler
                              information from PubNub service or cached
                              information from previous module call.
        """
        self.update(event_handler)

    def _default_handler_payload(self):
        """Compose default payload for event handler create / update.

        Payload include application-wide information and doesn't depend
        from particular event handler configuration.
        :rtype:  dict
        :return: Initial payload dictionary which can be used for event
                 handler manipulation requests.
        """
        return dict(key_id=self._keyset_id, block_id=self._block_id, type='js',
                    output="output-{}".format(random.random()),
                    log_level='debug')
