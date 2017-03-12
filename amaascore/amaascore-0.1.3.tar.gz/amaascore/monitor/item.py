import uuid

from amaascore.core.amaas_model import AMaaSModel


class Item(AMaaSModel):

    def __init__(self, asset_manager_id, item_class, item_type, item_level, item_source, message, item_id=None,
                 item_status='Open', asset_book_id=None, transaction_id=None, asset_id=None, item_date=None,
                 *args, **kwargs):

        self.asset_manager_id = asset_manager_id
        self.item_id = item_id or uuid.uuid4().hex
        self.item_class = item_class
        self.item_type = item_type
        self.item_level = item_level
        self.item_source = item_source
        self.message = message
        self.item_status = item_status
        self.asset_book_id = asset_book_id
        self.transaction_id = transaction_id
        self.asset_id = asset_id
        self.item_date = item_date
        super(Item, self).__init__(*args, **kwargs)
