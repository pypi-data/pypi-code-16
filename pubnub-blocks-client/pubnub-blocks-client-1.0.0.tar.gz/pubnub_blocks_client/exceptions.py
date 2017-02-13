"""Module contain set of exceptions which is used by PubNub BLOCKS module."""

# Error codes.
PN_AUTHORIZATION_MISSING_CREDENTIALS = 1000
PN_AUTHORIZATION_WRONG_CREDENTIALS = 1001
PN_KEYSET_BLOCK_EXISTS = 1002
PN_KEYSET_BLOCKS_FETCH_DID_FAIL = 1003
PN_BLOCK_EVENT_HANDLER_EXISTS = 1004
PN_BLOCK_CREATE_DID_FAIL = 1005
PN_BLOCK_UPDATE_DID_FAIL = 1006
PN_BLOCK_REMOVE_DID_FAIL = 1007
PN_BLOCK_START_STOP_DID_FAIL = 1008
PN_EVENT_HANDLER_MISSING_FIELDS = 1009
PN_EVENT_HANDLER_CREATE_DID_FAIL = 1010
PN_EVENT_HANDLER_UPDATE_DID_FAIL = 1011
PN_EVENT_HANDLER_REMOVE_DID_FAIL = 1012


class GeneralPubNubError(Exception):
    """Base exception for errors issued by PubNub BLOCKS client."""

    def __init__(self, message, code=-1):
        """Construct base exception.

        :type message:  str
        :param message: Reference on message which describe error reason.
        :type code:     int
        :param code:    Reference on error code to make error handling
                        easier.

        :rtype:  GeneralPubNubError
        :return: Initialized and ready to use exception.
        """
        final_message = message+' (code: {0}).'.format(code)
        super(GeneralPubNubError, self).__init__(final_message)
        self.code = code


class AccountError(GeneralPubNubError):
    """Exception which is used to report various account data access
    issues.
    """

    def __init__(self, message, code=-1):
        """Construct base exception.

        :type message:  str
        :param message: Reference on message which describe error reason.
        :type code:     int
        :param code:    Reference on error code to make error handling
                        easier.

        :rtype:  AccountError
        :return: Initialized and ready to use exception.
        """
        super(AccountError, self).__init__(message, code=code)
        self.owner = None
        """:type : str"""
        self.application = None
        """:type : str"""

    @classmethod
    def missing_credentials(cls, credentials):
        """Construct missing credentials error.

        :type credentials:  list[str]
        :param credentials: List of missed credentials.

        :rtype:  AuthorizationError
        :return: Initialized and ready to use exception.
        """
        return AccountError('Authorization error: missing credentials: '
                            '{0}'.format(', '.join(credentials)),
                            code=PN_AUTHORIZATION_MISSING_CREDENTIALS)

    @classmethod
    def wrong_credentials(cls, service_response):
        """Construct wrong credentials error.

        :type service_response:  str
        :param service_response: Reference on service response with reason
                                 description.

        :rtype:  AuthorizationError
        :return: Initialized and ready to use exception.
        """
        return AccountError(service_response,
                            code=PN_AUTHORIZATION_WRONG_CREDENTIALS)


class KeysetError(GeneralPubNubError):
    """Exception which is used to report various keyset data access
    issues.
    """

    def __init__(self, message, code=-1):
        """Construct base exception.

        :type message:  str
        :param message: Reference on message which describe error reason.
        :type code:     int
        :param code:    Reference on error code to make error handling
                        easier.

        :rtype:  KeysetError
        :return: Initialized and ready to use exception.
        """
        super(KeysetError, self).__init__(message, code=code)
        self.block = None
        """:type : str"""
        self.keyset = None
        """:type : str"""

    @classmethod
    def block_already_exists(cls, keyset, block):
        """Construct block already exists error.

        Raise error in case if user tried to add new block which has same
        name as the one which is already registered with keyset.
        :type keyset:  str
        :param keyset: Reference on name of keyset for which block addition
                       attempt did fail.
        :type block:   str
        :param block:  Reference on name of block which already exists for
                       keyset.

        :rtype:  KeysetError
        :return: Initialized and ready to use exception.
        """
        error = KeysetError('Block \'{0}\' already exists for '.format(block) +
                            '\'{0}\' keyset. If previous '.format(keyset) +
                            'block with same name has been removed, make sure '
                            'account has been saved before trying to add new '
                            'block. Also it is possible to retrieve existing '
                            'block model and update it if required',
                            code=PN_KEYSET_BLOCK_EXISTS)
        error.block = block
        error.keyset = keyset

        return error

    @classmethod
    def unable_to_fetch_blocks(cls, keyset, description):
        """Construct block creation error.

        Raise error if PubNub REST API will return error while creating
        new block.
        :type keyset:       str
        :param keyset:      Reference on name of keyset for which load of
                            list of blocks attempt did fail.
        :type description:  str
        :param description: Reference on PubNub service error description.

        :rtype:  KeysetError
        :return: Initialized and ready to use exception.
        """
        description = description or 'unknown reasons'
        error = KeysetError('Unable to fetch list of blocks for ' +
                            '{0}\' keyset: {1}'.format(keyset, description),
                            code=PN_KEYSET_BLOCKS_FETCH_DID_FAIL)
        error.keyset = keyset

        return error


class BlockError(GeneralPubNubError):
    """Exception which is used to report various keyset data access
    issues.
    """

    def __init__(self, message, code=-1):
        """Construct base exception.

        :type message:  str
        :param message: Reference on message which describe error reason.
        :type code:     int
        :param code:    Reference on error code to make error handling
                        easier.

        :rtype:  BlockError
        :return: Initialized and ready to use exception.
        """
        super(BlockError, self).__init__(message, code=code)
        self.block = None
        """:type : str"""
        self.event_handler = None
        """:type : str"""
        self.stack = None
        """:type : str"""

    @classmethod
    def event_handler_exists(cls, block, event_handler):
        """Construct event handler exists error.

        Raise error in case if user tried to add new event handler which
        has same name as the one which is already registered with block.
        :type block:           str
        :param block:          Reference on name of block which for which
                               event handler addition attempt did fail.
        :type event_handler:   str
        :param event_handler:  Reference on name of event handler which
                               already exists for block.

        :rtype:  BlockError
        :return: Initialized and ready to use exception.
        """
        error = BlockError('Event handler \'{0}\' '.format(event_handler) +
                           'already exists for \'{0}\' block. '.format(block) +
                           'If previous event handler with same name has been '
                           'removed, make sure account has been saved before '
                           'trying to add new event handler. Also it is '
                           'possible to retrieve existing event handler model '
                           'and update it if required',
                           code=PN_BLOCK_EVENT_HANDLER_EXISTS)
        error.block = block
        error.event_handler = event_handler

        return error

    @classmethod
    def block_create_error(cls, block, description):
        """Construct block creation error.

        Raise error if PubNub REST API will return error while creating
        new block.
        :type block:        str
        :param block:       Reference on name of block for which creation
                            did fail.
        :type description:  str
        :param description: Reference on PubNub service error description.

        :rtype:  BlockError
        :return: Initialized and ready to use exception.
        """
        error = BlockError('Unable create \'{0}\' block: '.format(block) +
                           '{0}'.format(description or 'unknown reasons'),
                           code=PN_BLOCK_CREATE_DID_FAIL)
        error.block = block

        return error

    @classmethod
    def block_update_error(cls, block, description):
        """Construct block update error.

        Raise error if PubNub REST API will return error while tried to
        update block.
        :type block:        str
        :param block:       Reference on name of block which can't be
                            updated.
        :type description:  str
        :param description: Reference on PubNub service error description.

        :rtype:  BlockError
        :return: Initialized and ready to use exception.
        """
        error = BlockError('Unable to update \'{0}\' block: '.format(block) +
                           '{0}'.format(description or 'unknown reasons'),
                           code=PN_BLOCK_UPDATE_DID_FAIL)
        error.block = block

        return error

    @classmethod
    def block_remove_error(cls, block, description):
        """Construct block removal error.

        Raise error if PubNub REST API will return error while tried to
        remove block.
        :type block:        str
        :param block:       Reference on name of block which can't be
                            deleted.
        :type description:  str
        :param description: Reference on PubNub service error description.

        :rtype:  BlockError
        :return: Initialized and ready to use exception.
        """
        error = BlockError('Unable to remove \'{0}\' block: '.format(block) +
                           '{0}'.format(description or 'unknown reasons'),
                           code=PN_BLOCK_REMOVE_DID_FAIL)
        error.block = block

        return error

    @classmethod
    def start_stop_did_fail(cls, block, description, stack):
        """Construct block start/stop error.

        Raise error in case if user during block launch/stop error
        occurred.
        :type block:        str
        :param block:       Reference on name of block which tried to
                            start/stop and failed.
        :type description:  str
        :param description: Reference on message which clarify what exactly
                            went wrong.
        :type stack:        str
        :param stack:       Reference on event handler error stack (if
                            there is syntax error in event handler code).

        :rtype:  BlockError
        :return: Initialized and ready to use exception.
        """
        error = BlockError(description, code=PN_BLOCK_START_STOP_DID_FAIL)
        error.block = block
        error.stack = stack

        return error


class EventHandlerError(GeneralPubNubError):
    """Exception which is used to report various event handler data access
    issues.
    """

    def __init__(self, message, code=-1):
        """Construct base exception.

        :type message:  str
        :param message: Reference on message which describe error reason.
        :type code:     int
        :param code:    Reference on error code to make error handling
                        easier.

        :rtype:  EventHandlerError
        :return: Initialized and ready to use exception.
        """
        super(EventHandlerError, self).__init__(message, code=code)
        self.event_handler = None
        """:type : str"""

    @classmethod
    def event_handler_missing_fields(cls, event_handler, fields):
        """Construct event handler creation error.

        Raise if there is missing event handler fields which is required to
        create new one.
        :type event_handler:  str
        :param event_handler: Reference on name of event handler for which
                              creation did fail.
        :type fields:         list[str]
        :param fields:        Reference on list of missing field names.

        :rtype:  EventHandlerError
        :return: Initialized and ready to use exception.
        """
        error = EventHandlerError('Unable create event handler w/o following '
                                  'fields: {0}.'.format(', '.join(fields)),
                                  code=PN_EVENT_HANDLER_MISSING_FIELDS)
        error.event_handler = event_handler

        return error

    @classmethod
    def event_handler_create_error(cls, event_handler, description):
        """Construct event handler creation error.

        Raise error if PubNub REST API will return error while creating
        new event handler.
        :type event_handler:  str
        :param event_handler: Reference on name of event handler for which
                              creation did fail.
        :type description:    str
        :param description:   Reference on PubNub service error
                              description.

        :rtype:  EventHandlerError
        :return: Initialized and ready to use exception.
        """
        description = description or 'unknown reasons'
        msg = ('Unable create \'{0}\' event handler: '.format(event_handler) +
               '{0}'.format(description))
        error = EventHandlerError(msg, code=PN_EVENT_HANDLER_CREATE_DID_FAIL)
        error.event_handler = event_handler

        return error

    @classmethod
    def event_handler_update_error(cls, event_handler, description):
        """Construct event handler update error.

        Raise error if PubNub REST API will return error while tried to
        update event handler.
        :type event_handler:  str
        :param event_handler: Reference on name of block which can't be
                              updated.
        :type description:    str
        :param description:   Reference on PubNub service error
                              description.

        :rtype:  EventHandlerError
        :return: Initialized and ready to use exception.
        """
        msg = ('Unable to update \'{0}\' block: '.format(event_handler) +
               '{0}'.format(description or 'unknown reasons'))
        error = EventHandlerError(msg, code=PN_EVENT_HANDLER_UPDATE_DID_FAIL)
        error.event_handler = event_handler

        return error

    @classmethod
    def event_handler_remove_error(cls, event_handler, description):
        """Construct event handler removal error.

        Raise error if PubNub REST API will return error while tried to
        remove event handler.
        :type event_handler:  str
        :param event_handler: Reference on name of block which can't be
                              deleted.
        :type description:    str
        :param description:   Reference on PubNub service error
                              description.

        :rtype:  EventHandlerError
        :return: Initialized and ready to use exception.
        """
        msg = ('Unable to remove \'{0}\' block: '.format(event_handler) +
               '{0}'.format(description or 'unknown reasons'))
        error = EventHandlerError(msg, code=PN_EVENT_HANDLER_REMOVE_DID_FAIL)
        error.event_handler = event_handler

        return error
