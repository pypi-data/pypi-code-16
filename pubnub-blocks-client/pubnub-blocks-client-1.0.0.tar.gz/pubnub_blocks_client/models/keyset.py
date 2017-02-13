"""Keyset representation model."""
from pubnub_blocks_client.exceptions import KeysetError
from pubnub_blocks_client.utils import value_for_key
from pubnub_blocks_client.models.model import Model
from pubnub_blocks_client.models.block import Block
import pubnub_blocks_client.core.api as api


class Keyset(Model):
    """PubNub application's keyset representation model."""

    def __init__(self, keyset, access, initial=False):
        """Construct application's keyset model using service response.

        :type keyset:   dict
        :param keyset:  PubNub service response with information about
                        particular application's keyset.
        :type access:   AccountAccess
        :param: access  Reference on account access information.
        :type initial:  bool
        :param initial: Whether keyset created during account
                        initialization from the scratch (not from cache).

        :rtype:  Keyset
        :return: Initialized keyset model.
        """
        super(Keyset, self).__init__(additional_fields=['pnm_blocks'])
        self._changed = False
        self._access = access
        self._will_add_blocks = False
        self._will_remove_blocks = False
        self._blocks = None
        """:type: dict[str : Block]"""
        self._process_data(keyset=keyset, initial=initial)

    def _get_non_property(self, name):
        """Retrieve list of serialized blocks.

        Retrieve pre-processed (serialized) list of blocks which is
        registered for keyset.
        :type name:  str
        :param name: Reference on name which represent blocks field.

        :return: Serialized blocks list.
        """
        return list(dict(block) for block in self.blocks if block.uid != -1)

    @property
    def uid(self):
        """Stores reference on unique keyset identifier.

        :rtype:  int
        :return: Reference on unique keyset identifier. '-1' will be
                 returned in case if keyset model configuration not
                 completed.
        """
        return self.get_property('id', default=-1)

    @property
    def name(self):
        """Stores reference on keyset name.

        :rtype:  str
        :return: Reference on keyset name. 'None' in case if keyset model
                 configuration not completed.
        """
        return self.get_property('properties.name', is_path=True)

    @property
    def publish_key(self):
        """Stores reference on keyset publish key.

        :rtype:  str
        :return: Reference on publish key. 'None' in case if keyset model
                 configuration not completed.
        """
        return self.get_property('publish_key')

    @property
    def subscribe_key(self):
        """Stores reference on keyset subscribe key.

        :rtype:  str
        :return: Reference on subscribe key. 'None' in case if keyset model
                 configuration not completed.
        """
        return self.get_property('subscribe_key')

    @property
    def secret_key(self):
        """Stores reference on keyset secret key.

        :rtype:  str
        :return: Reference on secret key. 'None' in case if keyset model
                 configuration not completed.
        """
        return self.get_property('secret_key')

    @property
    def blocks(self):
        """Stores reference on list of block models.

        All blocks which is registered for this keyset represented by
        models and stored in this property.
        :rtype:  list[Block]
        :return: List of block models.
        """
        # Fetch blocks list if it is required.
        self._fetch_blocks_if_required()

        return list(self._blocks.values())

    @property
    def will_change(self):
        """Stores whether some portion of keyset's data will be changed.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if keyset or blocks data will change during
                 save process.
        """
        will_change = False
        if not self.changed:
            will_change = self._will_add_blocks or self._will_remove_blocks
            for block in self.blocks:
                will_change = will_change or block.will_change
                if will_change:
                    break

        return will_change

    @property
    def changed(self):
        """Check whether keyset's data has been changed or not.

        Whether something has been changed in keyset or it's components
        during last save operation.
        NOTE: Value will be reset as soon as new modifications will be done
        and will be set to proper value only after save operation
        completion.
        :rtype:  bool
        :return: 'True' in case if keyset or block data has been modified.
        """
        changed = self._changed
        for block in self.blocks:
            changed = changed or block.changed
            if changed:
                break

        return changed

    def block_exists(self, name):
        """Check whether specific block exists in keyset or not.

        :type name:  str
        :param name: Reference on block name for which existence should
                     be checked.

        :rtype:  bool
        :return: 'True' in case if specified block registered for receiver
                 keyset.
        """
        # Fetch blocks list if it is required.
        self._fetch_blocks_if_required()

        return name is not None and name in self._blocks

    def block(self, name):
        """Retrieve reference on specific block which is created for
         receiver keyset.

        :type name:  str
        :param name: Reference on block name for which model should be
                     retrieved from list of application's keysets.

        :raises: KeysetError in case if there is no block with specified
                 name.

        :rtype:  Block
        :return: Reference on one of keyset's blocks.
        """
        # Fetch blocks list if it is required.
        self._fetch_blocks_if_required()

        return value_for_key(self._blocks, name)

    def add_block(self, block):
        """Add new block to keyset.

        Create new block by user request and store it in keyset model.
        :type block:  Block
        :param block: Reference on initialized new block which should be
                      created.

        :raise: KeysetError in case if tried to add block which already
                exists or has been marked for removal but not saved yet.
        """
        # Fetch blocks list if it is required.
        self._fetch_blocks_if_required()

        if not self.block_exists(block.name):
            self._will_add_blocks = True
            self._changed = False
            block.update_block(keyset=self, access=self._access)
            self._blocks[block.name] = block
        else:
            raise KeysetError.block_already_exists(self.name, block=block.name)

    def replace_block(self, old_name, block, new_name=None):
        """Update block which is stored under specified keys.

        WARNING: This method should be used internally by module itself.

        :type old_name:  str
        :param old_name: Reference on name under which 'block' should be
                         stored.
        :type block:     Block
        :param block:    Reference on Block model instance which should be
                         placed under specified 'old_name' or 'new_name'
                         (if specified).
        :type new_name:  str
        :param new_name: Reference on name under which 'block' should be
                         stored. If specified, block which is stored under
                         'old_name' will be removed.
        """
        # Fetch blocks list if it is required.
        self._fetch_blocks_if_required()

        if new_name and self.block_exists(old_name):
            del self._blocks[old_name]
        self._blocks[new_name or old_name] = block

    def remove_block(self, block):
        """Remove block from keyset.

        Stop and remove target block if it exists.
        :type block:  Block
        :param block: Reference on Block model instance which should be
                      removed.
        """
        # Fetch blocks list if it is required.
        self._fetch_blocks_if_required()

        if self.block_exists(block.name):
            self._will_remove_blocks = True
            self._changed = False
            block.delete()

    def save(self):
        """Store any changes to keyset and/or blocks."""
        blocks_for_removal = list(block.name for block in self.blocks
                                  if block.should_delete)
        for block in self.blocks:
            block.save()
        for block_name in blocks_for_removal:
            del self._blocks[block_name]
        if blocks_for_removal or self._will_add_blocks:
            self._changed = True
        self._will_remove_blocks = False
        self._will_add_blocks = False

    def _fetch_blocks_if_required(self):
        """Fetch keyset's blocks if required.

        In case if this is first time when keyset is used blocks should be
        retrieved.
        """
        if self._blocks is None:
            response, error = api.blocks(self._access.token,
                                         keyset_id=self.uid)
            if error is not None:
                description = value_for_key(error, 'message')
                params = dict(keyset=self.name, description=description)
                raise KeysetError.unable_to_fetch_blocks(**params)
            self._process_data(blocks=response)

    def _process_data(self, keyset=None, blocks=None, initial=False):
        """Process fetched keyset data.

        Process received keyset data to complete model configuration.
        :type keyset:   dict
        :param keyset:  Reference on dictionary which contain information
                        about application's keyset.
        :type blocks:   list[dict]
        :param blocks:  Reference on list of dictionaries each of which
                        represent block with event handlers.
        :type initial:  bool
        :param initial: Whether keyset created during account
                        initialization from the scratch (not from cache).
        """
        b_data = None
        keyset = keyset or dict()
        if 'pnm_blocks' in keyset:
            b_data = keyset.pop('pnm_blocks')

        # Store keyset information.
        if keyset:
            self.update(keyset)

        # Process blocks data.
        if blocks is not None:
            if self._blocks is None:
                self._blocks = dict()
            for blk in blocks:
                block = Block()
                block.update_block(keyset=self, block=blk, access=self._access)
                self._blocks[block.name] = block
        if not initial and b_data is not None:
            self._process_data(blocks=b_data, initial=initial)
