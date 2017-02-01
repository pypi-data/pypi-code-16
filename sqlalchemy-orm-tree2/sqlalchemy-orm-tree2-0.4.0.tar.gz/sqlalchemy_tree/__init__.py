#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree
    ~~~~~~~~~~~~~~~

    An implementation for SQLAlchemy-based applications of the
    nested-sets/modified-pre-order-tree-traversal technique for storing
    hierarchical data in a relational database.

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>
    :license: BSD, see LICENSE for more details.
"""

from operator import attrgetter

from .exceptions import InvalidMoveError
from .manager import TreeClassManager, TreeInstanceManager, TreeManager
from .options import TreeOptions
from .orm import TreeMapperExtension, TreeSessionExtension, \
    DeclarativeMeta
from .types import TreeDepthType, TreeEndpointType, TreeIdType, \
    TreeIntegerType, TreeLeftType, TreeRightType


_nonexistent = object()
def _iter_current_next(sequence):
    """
    Generate `(current, next)` tuples from sequence. Last tuple will
    have `_nonexistent` object at the second place.

    >>> x = _iter_current_next('1234')
    >>> next(x), next(x), next(x)
    (('1', '2'), ('2', '3'), ('3', '4'))
    >>> next(x) == ('4', _nonexistent)
    True
    >>> list(_iter_current_next(''))
    []
    >>> list(_iter_current_next('1')) == [('1', _nonexistent)]
    True
    """
    iterator = iter(sequence)
    current_item = next(iterator)
    while current_item != _nonexistent:
        try:
            next_item = next(iterator)
        except StopIteration:
            next_item = _nonexistent
        yield (current_item, next_item)
        current_item = next_item


def _recursive_iterator(sequence, is_child_func):
    """
    Make a recursive iterator from plain sequence using :attr:`is_child_func`
    to determine parent-children relations. Works right only if used in
    depth-first recursive consumer.

    :param is_child_func:
        a callable object which accepts two positional arguments and
        returns the number of levels between the first argument value and
        the second second argument value, or 0 if the second argument is
        not a child of the first.

    >>> is_child_func = lambda parent, child: child > parent
    >>> def listify(seq):
    ...     return [(node, listify(children)) for node, children in seq]
    >>> listify(_recursive_iterator('ABCABB', is_child_func))
    [('A', [('B', [('C', [])])]), ('A', [('B', []), ('B', [])])]
    >>> listify(_recursive_iterator('', is_child_func))
    []
    >>> next(_recursive_iterator('A', is_child_func))
    ('A', ())
    >>> next(_recursive_iterator('AB', is_child_func)) # doctest: +ELLIPSIS
    ('A', <generator object ...>)
    """
    current_next_iterator = _iter_current_next(sequence)
    item = {}
    is_parent_of_next = lambda node: \
            item['next'] is not _nonexistent \
            and is_child_func(node, item['next'])

    def consume_below_level(node, level):
        while item['next'] is not _nonexistent and is_child_func(node, item['next']) > level:
            item['current'], item['next'] = next(current_next_iterator)

    def step():
        item['current'], item['next'] = next(current_next_iterator)

        if is_parent_of_next(item['current']):
            return (item['current'], children_generator(item['current']))
        else:
            return (item['current'], tuple())

    def children_generator(parent_node):
        while True:
            yield step()

            # If at this point the next item is further than 1 down the tree,
            # we know that the user did not consume other child iterators that
            # we gave him. Remove everything until we catch up to our level.
            consume_below_level(parent_node, 1)

            # Now that we are on our level, the next one is either a direct
            # child again, or we are finished with the children of this node.
            if not is_parent_of_next(parent_node):
                #q('%sbreaking out of child iter %s (%s) because of %s (%s)' % (parent_node.tree_depth*'    ', parent_node.linktext, parent_node.tree_depth, item['next'].linktext, item['next'].tree_depth))
                break

    while True:
        node, children = step()
        yield node, children

        consume_below_level(node, 0)


def tree_recursive_iterator(flat_tree, class_manager):
    """
    Make a recursive iterator from plain tree nodes sequence (`Query`
    instance for example). Generates two-item tuples: node itself
    and it's children collection (which also generates two-item tuples...)
    Children collection evaluates to ``False`` if node has no children
    (it is zero-length tuple for leaf nodes), else it is a generator object.

    :param flat_tree: plain sequence of tree nodes.
    :param class_manager: instance of :class:`MPClassManager`.

    Can be used when it is simpler to process tree structure recursively.
    Simple usage example::

        def recursive_tree_processor(nodes):
            print '<ul>'
            for node, children in nodes:
                print '<li>%s' % node.name,
                if children:
                    recursive_tree_processor(children)
                print '</li>'
            print '</ul>'

        query = root_node.mp.query_descendants(and_self=True)
        recursive_tree_processor(
            sqlamp.tree_recursive_iterator(query, Node.mp)
        )

    .. versionchanged::
        0.6
        Before this function was sorting `flat_tree` if it was a query-object.
        Since 0.6 it doesn't do it, so make sure that `flat_tree` is properly
        sorted. The best way to achieve this is using queries returned from
        public API methods of :class:`MPClassManager` and
        :class:`MPInstanceManager`.

    .. warning:: Process `flat_tree` items once and sequentially so works
      right only if used in depth-first recursive consumer.
    """
    opts = class_manager._tree_options
    tree_id = attrgetter(opts.tree_id_field.name)
    depth = attrgetter(opts.depth_field.name)
    def is_child(parent, child):
        if  tree_id(parent) != tree_id(child) or depth(child) <= depth(parent):
            return 0
        return depth(child) - depth(parent)
    return _recursive_iterator(flat_tree, is_child)
