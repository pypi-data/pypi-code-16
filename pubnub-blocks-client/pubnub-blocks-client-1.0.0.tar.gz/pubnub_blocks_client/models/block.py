"""Block representation model."""
from pubnub_blocks_client.models.event_handler import EventHandler
from pubnub_blocks_client.models.model import MutableModel
from pubnub_blocks_client.exceptions import BlockError
from pubnub_blocks_client.utils import value_for_key
import pubnub_blocks_client.core.api as api


class Block(MutableModel):
    """PubNub block representation model."""

    def __init__(self, name=None, description=None):
        """Construct block model using service response.

        :type name:         str
        :param name:        Reference on name of block which should be
                            created.
        :type description:  str
        :param description: Reference on bew block description.

        :rtype:  Block
        :return: Initialized block model.
        """
        super(Block, self).__init__(additional_fields=['event_handlers'])
        self._changed = False
        self._access = None
        """:type: AccountAccess"""
        self._keyset = None
        """:type: Keyset"""
        self._will_remove_event_handlers = False
        self._will_add_event_handlers = False
        self._event_handlers = dict()
        self._should_delete = False
        if name or description:
            self.name = name
            self.description = description

    def _get_non_property(self, name):
        """Retrieve list of serialized event handlers.

        Retrieve pre-processed (serialized) list of event handlers which is
        registered for block.
        :type name:  str
        :param name: Reference on name which represent event handlers
                     field.

        :return: Serialized event handlers list.
        """
        return list(dict(handler) for handler in self.event_handlers
                    if handler.uid != -1)

    @property
    def uid(self):
        """Stores reference on unique block's identifier.

        :rtype:  int
        :return: Reference on unique block's identifier. '-1' will be
                 returned in case if block model configuration not
                 completed.
        """
        return self.get_property('id', default=-1)

    @property
    def template_id(self):
        """Stores reference on unique identifier of template block.

        Template blocks used to copy their configuration into new block.
        :rtype:  int
        :return: Reference on template block unique identifier. '-1' will
                 be returned in case if block created from scratch.
        """
        return self.get_property('cloned_id', default=-1)

    @property
    def name(self):
        """Stores reference on block's name.

        :rtype:  str | None
        :return: Reference on block's name. 'None' will be returned in case
                 if block model configuration not completed.
        """
        return self.get_property('name', original=False)

    @name.setter
    def name(self, name):
        """Update block's name.

        :type name:  str
        :param name: Reference on new block name.
        """
        original_name = self.get_property('name', original=False)
        self.set_property('name', value=name)
        if self.data_changed('name') and self._keyset:
            self._keyset.replace_block(old_name=original_name, block=self,
                                       new_name=name)

    @property
    def description(self):
        """Stores reference on block's description.

        :rtype:  str | None
        :return: Reference on block's description. 'None' will be returned
                 in case if block model configuration not completed.
        """
        return self.get_property('description', original=False)

    @description.setter
    def description(self, description):
        """Update block's description.

        :type description:  str
        :param description: Reference on new block's description.
        """
        self.set_property('description', value=description)

    @property
    def state(self):
        """Stores reference on current block's state.

        :rtype:  str | None
        :return: Reference on block's state. 'None' will be returned in
                 case if block model configuration not completed.
        """
        return self.get_property('state')

    @property
    def target_state(self):
        """Stores reference on target block's state.

        :rtype:  str | None
        :return: Reference on block's state. 'None' will be returned in
                 case if block model configuration not completed.
        """
        return self.get_property('intended_state')

    @target_state.setter
    def target_state(self, target_state):
        """Update block's target state.

        :type target_state:  str
        :param target_state: Reference on new block's target state.
        """
        self.set_property('intended_state', value=target_state)

    @property
    def publish_key(self):
        """Stores reference on block publish key.

        :rtype:  str
        :return: Reference on publish key. 'None' will be returned in case
                 if block model configuration not completed.
        """
        return self.get_property('pub_key')

    @property
    def subscribe_key(self):
        """Stores reference on block subscribe key.

        :rtype:  str
        :return: Reference on subscribe key. 'None' will be returned in
                 case if block model configuration not completed.
        """
        return self.get_property('sub_key')

    @property
    def should_delete(self):
        """Stores whether block should be removed during save operation or
        not.

        Block removal will happen at the same moment when account will be
        asked to 'save' changes.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if block has been marked for removal.
        """
        return self._should_delete

    @property
    def event_handlers(self):
        """Stores reference on list of block's event handler models.

        All event handlers which is registered for this block represented
        by models and stored in this property.
        :rtype:  list[EventHandler]
        :return: List of block models.
        """
        return list(self._event_handlers.values())

    @property
    def _payload(self):
        """Stores reference on block data which is structured according to
        PubNub service requirements.

        :rtype:  dict
        :return: Block information in format which is known to PubNub
                 service.
        """
        payload = dict()
        if not self.is_empty:
            payload.update(key_id=self._keyset.uid, block_id=self.uid,
                           name=self.name, description=self.description)
            if value_for_key(payload, 'description') is None:
                payload['description'] = ('No description provided for this '
                                          'block.')

        return payload

    @property
    def will_change(self):
        """Stores whether some portion of block's data will be changed.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if block or event handler data will change
                 during save process.
        """
        will_change = False
        if not self.changed:
            will_change = (self._will_add_event_handlers
                           or self._will_remove_event_handlers
                           or self._should_create() or self.should_delete
                           or self._should_save())
            for event_handler in self.event_handlers:
                will_change = will_change or event_handler.will_change
                if will_change:
                    break

        return will_change

    @property
    def changed(self):
        """Check whether block's data has been changed or not.

        Whether something has been changed in block or it's components
        during last save operation.
        NOTE: Value will be reset as soon as new modifications will be done
        and will be set to proper value only after save operation
        completion.
        :rtype:  bool
        :return: 'True' in case if block or event handlers data has been
                 modified.
        """
        changed = self._changed
        for event_handler in self.event_handlers:
            changed = changed or event_handler.changed
            if changed:
                break

        return changed

    def update_block(self, keyset, block=None, access=None):
        """Update block information.

        Update allow to complete block instance initialization and link it
        with keyset.
        :type keyset:  Keyset
        :param keyset: Reference on keyset model to which block belong.
        :type block:   dict
        :param block:  PubNub service response with information about
                       particular block.
        :type access:  AccountAccess
        :param access: Reference on account access information.

        :rtype:  Block
        :return: Initialized block model.
        """
        if access:
            self._access = access
        if keyset:
            self._keyset = keyset
        if block:
            self._process_data(block)
        for event_handler in self.event_handlers:
            event_handler.update_event_handler(block_id=self.uid,
                                               keyset_id=self._keyset.uid,
                                               access=self._access)

    def start(self):
        """Start block if possible.

        Block start request will be sent only if target state not equal to
        'running'.
        """
        self.target_state = 'running'

    def stop(self):
        """Stop block if possible.

        Block stop request will be sent only if target state not equal to
        'stopped'.
        """
        self.target_state = 'stopped'

    def delete(self):
        """Remove block from keyset."""
        self._should_delete = True

    def event_handler_exists(self, name):
        """Check whether specific event handler exists in block or not.

        :type name:  str
        :param name: Reference on name of event handler for which existence
                     should be checked.

        :rtype:  bool
        :return: 'True' in case if specified event handler registered for
                 receiver block.
        """
        return name is not None and name in self._event_handlers

    def event_handler(self, name):
        """Retrieve reference on specific event handler which is registered
        for receiver block.

        :type name:  str
        :param name: Reference on name of event handler for which model
                     should be retrieved from list of block handlers.

        :rtype:  EventHandler
        :return: Reference on event handler model or 'None' in case if
                 there is no event handler with specified name.
        """
        return value_for_key(self._event_handlers, name)

    def add_event_handler(self, event_handler):
        """Add new event handler into block.

        :type event_handler:  EventHandler
        :param event_handler: Reference on new initialized event handler
                              model which should be added to block after
                              save process completion.

        :raise: BlockError in case if tried to add event handler which
                already exists or has been marked for removal but not saved
                yet.
        """
        if not self.event_handler_exists(event_handler.name):
            self._will_add_event_handlers = True
            self._changed = False
            event_handler.update_event_handler(block_id=self.uid,
                                               keyset_id=self._keyset.uid,
                                               access=self._access)
            self._event_handlers[event_handler.name] = event_handler
        else:
            name = event_handler.name
            raise BlockError.event_handler_exists(self.name,
                                                  event_handler=name)

    def delete_event_handler(self, event_handler):
        """Remove existing event handler from block.

        :type event_handler:  EventHandler
        :param event_handler: Reference on existing event handler model
                              which should be removed from block after save
                              process completion.
        """
        if self.event_handler_exists(event_handler.name):
            self._will_remove_event_handlers = True
            self._changed = False
            event_handler.delete()

    def save(self):
        """Save pending block and event handler changes.

        Depending on whether block existed before or not it may be created
        and updated if required.
        """
        will_change = self.will_change
        stop_for_update = self._block_stop_require_stop()
        block_data = self._payload
        if self._should_create():
            block_data.update(self._create_block(block_data))
        elif self.should_delete:
            self._delete_block()
        elif self._should_save():
            params = dict(payload=block_data, stop_for_updates=stop_for_update)
            block_data = self._save_changes(**params)
        elif stop_for_update:
            # Stop block in case if event_handlers modification is
            # required.
            self._change_block_state(state='stopped',
                                     update_cached_state=False)

        if will_change:
            self._will_add_event_handlers = False
            self._will_remove_event_handlers = False
            self._changed = True
            if not self.should_delete:
                if self._should_create():
                    block_data.update(dict(intended_state='stopped',
                                           state='stopped'))
                self._process_data(block_data)

        event_handlers_for_removal = list(eh.name for eh in self.event_handlers
                                          if eh.should_delete)
        for event_handler in self.event_handlers:
            event_handler.save()
        for event_handler_name in event_handlers_for_removal:
            del self._event_handlers[event_handler_name]
        if event_handlers_for_removal or self._will_add_event_handlers:
            self._will_add_event_handlers = False
            self._will_remove_event_handlers = False
            self._changed = True

        if stop_for_update:
            if not self._event_handlers:
                self.target_state = 'stopped'
            state = self.get_property('intended_state', original=False)
            self._change_block_state(state=state)

    def _create_block(self, payload):
        """Create new block and register with keyset.

        Send request to create block and handle error if any will happen.
        :type payload:  dict
        :param payload: Reference on block payload which will be populated
                        with service response (contain base information
                        about new block).

        :rtype:  dict
        :return: Updated block payload.
        """
        response, error = api.create_block(self._access.token,
                                           keyset_id=self._keyset.uid,
                                           block_payload=payload)
        if error is None:
            response['block_id'] = response['id']
        else:
            description = value_for_key(error, 'message')
            raise BlockError.block_create_error(block=self.name,
                                                description=description)

        return response

    def _save_changes(self, payload, stop_for_updates):
        """Send block modifications to PubNub BLOCKS.

        Depending from whether event handlers require block stop or not
        it's operation state can be changed as well.
        :type payload:           dict
        :param payload:          Reference on payload for block with all
                                 modifications.
        :type stop_for_updates:  bool
        :param stop_for_updates: Whether block expected to stop to complete
                                 event handlers modification or not.
        """
        # Update block own information.
        error = None
        if self._should_save(['key_id', 'state', 'intended_state']):
            _, error = api.update_block(self._access.token, block_id=self.uid,
                                        keyset_id=self._keyset.uid,
                                        block_payload=payload)
            if error is not None:
                description = value_for_key(error, 'message')
                raise BlockError.block_update_error(block=self.name,
                                                    description=description)
            payload = self.mutable_data()
            payload.update(self._payload or dict())

        # Change block operation state as it has been requested by user.
        if not stop_for_updates and error is None:
            state = self.get_property('intended_state', mutated=True)
            self._change_block_state(state=state)

        return payload

    def _delete_block(self):
        """Remove existing block from keyset."""
        self._change_block_state(state='stopped', update_cached_state=False)
        _, error = api.delete_block(self._access.token, block_id=self.uid,
                                    keyset_id=self._keyset.uid)
        if error is not None:
            description = value_for_key(error, 'message')
            raise BlockError.block_remove_error(block=self.name,
                                                description=description)

    def _should_create(self):
        """Check whether block should be created or not.

        :rtype:  bool
        :return: 'True' in case if block unique identifier not assigned yet
                 which mean block new and should be created.
        """
        return self.uid == -1

    def _should_save(self, excluded_fields=None):
        """Check whether there is block changes which should be saved.

        :type excluded_fields:  list
        :param excluded_fields: List of fields which should be removed from
                                comparision.

        :rtype:  bool
        :return: 'True' in case if there is unsaved changes.
        """
        should_save = self._should_create()
        if not should_save:
            should_save = self.data_changed(ignored_fields=excluded_fields)

        return should_save

    def _block_stop_require_stop(self):
        """Check whether any block's event handler will change.

        Check whether any user-provided event handlers' data will cause
        their modification or not.
        :rtype:  bool
        :return: 'True' in case if any event handler change information
                 which require block stop.
        """
        require_stop = False
        for event_handler in self.event_handlers:
            require_stop = event_handler.change_require_block_stop
            if require_stop:
                break

        return require_stop

    def _change_block_state(self, state, update_cached_state=True):
        """Update actual block state.

        Perform block operation state change request and process service
        response.
        :type state:  str
        :param state: Reference on expected block operation state (running
                      or stopped).
        :type update_cached_state:  bool
        :param update_cached_state: Whether desired block state should be
                                    modified as well (the one
                                    which is asked by user during module
                                    configuration).
        """
        should_change_state = self.target_state != state or self.state != state
        if self._event_handlers and should_change_state:
            current_state = state if self.target_state == state else None
            operations = dict(running=api.start_block, stopped=api.stop_block)
            operation = operations[state]
            params = dict(token=self._access.token, keyset_id=self._keyset.uid,
                          block_id=self.uid, current_state=current_state)
            (timeout, error_reason, stack) = operation(**params)
            self._handle_block_state_change(state=state, timeout=timeout,
                                            error_reason=error_reason,
                                            stack=stack)
            self.set_property('intended_state', value=state, original=True)
            self.set_property('state', value=state, original=True)
            self.set_property('state', value=state)
            if update_cached_state:
                self.target_state = state

            if not current_state:
                self._changed = True

    def _process_data(self, block):
        """Process fetched block data.

        Process received block data to complete model configuration.
        :type block:  dict
        :param block: Reference on dictionary which contain information
                      about specific block.
        """
        event_handlers = None
        if 'event_handlers' in block:
            event_handlers = block.pop('event_handlers')
        for handler in event_handlers or list():
            event_handler = EventHandler()
            event_handler.update_event_handler(block_id=self.uid,
                                               keyset_id=self._keyset.uid,
                                               event_handler=handler,
                                               access=self._access)
            self._event_handlers[event_handler.name] = event_handler
        self.update(block)

    def _handle_block_state_change(self, state, timeout, error_reason, stack):
        """Handle block operation state change.

        :type state:         str
        :param state:        Target block state.
        :type timeout:       bool
        :param timeout:      Whether block state change failed by timeout
                             or not.
        :type error_reason:  str
        :param error_reason: Field contain error reason description (if
                             provided by PubNub service).
        :type stack:         str
        :param stack:        Reference on string which represent event
                             handler execution stack trace.
        """
        state = 'start' if state == 'running' else 'stop'
        err_msg = None
        if timeout:
            delay = (api.PN_BLOCK_STATE_CHECK_MAX_COUNT *
                     api.PN_BLOCK_STATE_CHECK_INTERVAL)
            err_msg = '\'{0}\' block not '.format(self.name) + \
                      '{0}\'ed in {1} seconds'.format(state, delay)
        elif stack:
            err_msg = 'Unable to {0} \'{1}\' '.format(state, self.name) + \
                      'block because of error: {0}'.format(error_reason)
        if err_msg:
            params = dict(block=self.name, description=err_msg, stack=stack)
            raise BlockError.start_stop_did_fail(**params)
