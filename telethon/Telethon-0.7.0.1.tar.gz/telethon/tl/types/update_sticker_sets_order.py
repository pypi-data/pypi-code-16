from telethon.tl.mtproto_request import MTProtoRequest


class UpdateStickerSetsOrder(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    updateStickerSetsOrder#0bb2d201 flags:None masks:flags.0?true order:Vector<long> = Update"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xbb2d201

    def __init__(self, order, masks=None):
        """
        :param masks: Telegram type: «true».
        :param order: Telegram type: «long». Must be a list.
        """
        super().__init__()

        self.masks = masks
        self.order = order

    def on_send(self, writer):
        writer.write_int(UpdateStickerSetsOrder.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.masks else 0
        writer.write_int(flags)

        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.order))
        for order_item in self.order:
            writer.write_long(order_item)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return UpdateStickerSetsOrder(None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        if (flags & (1 << 0)) != 0:
            self.masks = True  # Arbitrary not-None value, no need to read since it is a flag

        reader.read_int()  # Vector's constructor ID
        self.order = []  # Initialize an empty list
        order_len = reader.read_int()
        for _ in range(order_len):
            order_item = reader.read_long()
            self.order.append(order_item)

    def __repr__(self):
        return 'updateStickerSetsOrder#0bb2d201 flags:None masks:flags.0?true order:Vector<long> = Update'

    def __str__(self):
        return '(updateStickerSetsOrder (ID: 0xbb2d201) = (masks={}, order={}))'.format(str(self.masks), None if not self.order else [str(_) for _ in self.order])
