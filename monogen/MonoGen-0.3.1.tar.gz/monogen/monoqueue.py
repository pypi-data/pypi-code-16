from multiprocessing.managers import BaseManager

from monocle.utils import get_address
from monocle import sanitized as conf

class AccountManager(BaseManager): pass
AccountManager.register('extra_queue')
manager = AccountManager(address=get_address(), authkey=conf.AUTHKEY)
manager.connect()
extra_queue = manager.extra_queue()

def add_to_queue(account):
    account['time'] = 0
    account['captcha'] = False
    account['banned'] = False
    extra_queue.put(account)
