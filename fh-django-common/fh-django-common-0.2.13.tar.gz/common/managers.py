import datetime

from mptt.managers import TreeManager


class CustomTreeManager(TreeManager):

    epoch = datetime.datetime(1970, 1, 1)
    start = 1484159964477

    def _get_next_tree_id(self):
        return int((datetime.datetime.utcnow() - self.epoch).total_seconds() * 1000) - self.start
