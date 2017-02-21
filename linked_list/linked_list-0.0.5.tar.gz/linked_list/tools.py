from ll import LL
from dll import DLL


def pushback(lst, node):
    """This pushes an element to the end of the linked list.

    Has an :math:`\mathcal{O}(n)` where :math:`n` is the distance
    of *lst* from the end of the list. Also works with both
    :class:`~linked_list.ll.LL` and :class:`~linked_list.dll.DLL` classes.

    :param lst: Is a member of the list where we want to insert the *node*.
    :param node: The node which we want to insert into the linked list.

    :returns: Returns *node* after inserting it.

    :Example:

    >>> import linked_list as ll
    >>> lst = ll.LL(1)
    >>> node = ll.LL(2)
    >>> ll.pushback(lst, node)
    >>> lst.nxt.data
    2
    """
    tn = type(node)
    assert tn == type(lst)
    assert tn in (LL, DLL)

    curr = lst
    while curr.nxt is not None:
        curr = curr.nxt

    curr.nxt = node
    if tn == DLL:
        node.prev = curr

    return node


def pushfront(lst, node):
    """Pushes an element to the beginning of the linked list.

    Has an :math:`\mathcal{O}(n)` where :math:`n` is the distance
    of *lst* from the beginning of the list so most of the time 
    :math:`\mathcal{O}(1)`. This function only works with the 
    :class:`~linked_list.dll.DLL` class.

    :param lst: Is a member of the list where we want to insert the *node*.
    :param node: The node which we want to insert into the linked list.

    :returns: The *node* that we inserted.

    :Example:

    >>> import linked_list as ll
    >>> lst = ll.DLL(1)
    >>> node = ll.DLL(2)
    >>> ll.pushfront(lst, node)
    >>> lst.prev.data
    2
    """
    assert type(node) == type(lst)
    assert type(node) == DLL

    curr = lst
    while curr.prev is not None:
        curr = curr.prev

    curr.prev = node
    node.nxt = curr

    return node


def popfront(lst):
    """This pops the element from the beginning of the linked list.

    Has an :math:`\mathcal{O}(n)` where :math:`n` is the distance
    of *lst* from the beginning of the list. This works with the 
    :class:`~linked_list.dll.DLL` class.

    :param lst: Is a member of the list where we want to pop 
                the first element from.
    
    :returns: The first node.

    :Example:

    >>> import linked_list as ll
    >>> lst = ll.DLL(1)
    >>> node = ll.DLL(2)
    >>> ll.pushback(lst, node)
    >>> popfront(lst).data
    1
    """
    assert type(lst) == DLL
    if lst.prev is None:
        if lst.nxt is not None:
            lst.nxt.prev, lst.nxt = None, None
        return lst

    curr = lst
    while curr.prev is not None:
        curr = lst.prev

    curr.nxt.prev, curr.nxt, curr.prev = None, None, None
    return curr


def popback(lst):
    """This pops the element from the end of the linked list.

    Has an :math:`\mathcal{O}(n)` where :math:`n` is the distance
    of *lst* from the end of the list. This works with both the
    :class:`~linked_list.ll.LL` and  :class:`~linked_list.dll.DLL` 
    classes.

    :param lst: Is a member of the list where we want to pop 
                the last element from.
    
    :returns: Returns the last node.

    :Example:

    >>> import linked_list as ll
    >>> lst = ll.LL(1)
    >>> node = ll.LL(2)
    >>> ll.pushback(lst, node)
    >>> popback(lst).data
    2
    """
    tl = type(lst)
    assert tl in (LL, DLL)
    if lst.nxt is None:
        if tl == DLL and lst.prev is not None:
            lst.prev.nxt, lst.prev = None, None
        return lst

    prev = lst
    curr = lst.nxt
    while curr.nxt is not None:
        prev, curr = curr, curr.nxt

    prev.nxt = None
    if tl == DLL:
        curr.prev = None
    return curr


def delete(ancestor, node):
    """This deletes an element from the linked list.

    Has an :math:`\mathcal{O}(n)` where :math:`n` is the distance
    of *ancestor* from the *node*. Note that *ancestor* must come
    before *node* in the list. This works with both the
    :class:`~linked_list.ll.LL` and  :class:`~linked_list.dll.DLL` 
    classes.

    :param ancestor: Is a member of the list from where we want to
                     delete the *node* member.
    :param node: The node we want to delete from the list.

    :Example:

    >>> import linked_list as ll
    >>> lst = ll.LL(1)
    >>> node = ll.LL(2)
    >>> ll.pushback(lst, node)
    >>> ll.pushback(lst, ll.LL(3))
    >>> ll.delete(lst, node)
    >>> lst.nxt.data
    3
    """
    tn = type(node)
    assert tn == type(ancestor)
    assert tn in (LL, DLL)

    curr = ancestor
    while curr.nxt not in (None, node):
        curr = curr.nxt
    curr.nxt = node.nxt
    if tn == DLL and node.nxt is not None:
        node.nxt.prev = curr
    node.delete()

