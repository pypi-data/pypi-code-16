from base import LLBase


class DLL(LLBase):
    """Node class for the doubly linked list.
    
    The class has 3 members which are the following:

    - *data*: This is the the data that is stored in
              the current node. By default it's `None`.

    - *prev*: Points to the previous node in the 
              linked list or it's `None` if there
              is no previous node.

    - *nxt*: Points to the next node in the linked
             or it's `None` if there is no next node.        
    """
    data, nxt, prev = None, None, None
    
    def __init__(self, data=None, prev=None, nxt=None):
        self.data = data
        self.prev = prev
        self.nxt = nxt

    def delete(self):
        super(DLL, self).delete()
        self.prev = None

