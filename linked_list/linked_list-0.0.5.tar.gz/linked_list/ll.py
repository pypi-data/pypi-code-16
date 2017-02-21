from base import LLBase


class LL(LLBase):
    """Node class for the singly linked list.
    
    The class has 2 members which are the following:
               
    - *data*: This is the the data that is stored in
              the current node. By default it's `None`.
              
    - *nxt*: Points to the next node in the linked
             or it's `None` if there is no next node.
    """
    nxt = None
    data = None

    def __init__(self, data=None, nxt=None):
        self.nxt = nxt
        self.data = data

