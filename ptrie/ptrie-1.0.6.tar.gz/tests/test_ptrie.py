# -*- coding: utf-8 -*-
# test_ptrie.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,R0904,R0914,W0212,W0232,W0621

# Standard library imports
import copy
import pytest
# PyPI imports
from pmisc import AE, AI, AROPROP, RE
# Intra-package imports
import ptrie


###
# Fixtures
###
@pytest.fixture
def default_trees():
    """
    Provides a default tree to be used in testing the
    ptrie.TrieNode() class
    """
    #
    # Trie1             Trie2           Trie3       Trie4
    # t1l1 (*)          t2l1 (*)        t3l1 (*)    root
    # ├t1l2b1 (*)       ├t2l2b1 (*)                 ├branch1 (*)
    # │├t1l3b1a (*)     │├t2l3b1a (*)               │├leaf1
    # │├t1l3b1b (*)     │├t2l3b1b (*)               ││└subleaf1 (*)
    # │└t1l3b1c (*)     │└t2l3b1c (*)               │└leaf2 (*)
    # └t1l2b2 (*)       └t2l2b2 (*)                 │ └subleaf2
    #  ├t1l3b2a (*)        ├t2l3b2a (*)             └branch2
    #  ├t1l3b2b (*)        ├t2l3b2b (*)
    #  └t1l3b2c (*)        └t2l3b2c (*)
    t1obj = ptrie.Trie()
    t1obj.add_nodes({'name':'t1l1', 'data':'Trie 1, level 1'})
    t1obj.add_nodes([
        {'name':'t1l1.t1l2b1', 'data':'Trie 1, level 2, branch 1'},
        {'name':'t1l1.t1l2b2', 'data':'Trie 1, level 2, branch 2'},
        {
            'name':'t1l1.t1l2b1.t1l3b1a',
            'data':'Trie 1, level 3, branch 1, child a'
        },
        {
            'name':'t1l1.t1l2b1.t1l3b1b',
            'data':'Trie 1, level 3, branch 1, child b'
        },
        {
            'name':'t1l1.t1l2b1.t1l3b1c',
            'data':'Trie 1, level 3, branch 1, child c'
        },
        {
            'name':'t1l1.t1l2b2.t1l3b2a',
            'data':'Trie 1, level 3, branch 2, child a'
        },
        {
            'name':'t1l1.t1l2b2.t1l3b2b',
            'data':'Trie 1, level 3, branch 2, child b'
        },
        {
            'name':'t1l1.t1l2b2.t1l3b2c',
            'data':'Trie 1, level 3, branch 2, child c'
        },
    ])
    ###
    t2obj = ptrie.Trie()
    t2obj.add_nodes(
        {
            'name':'t2l1.t2l2b1.t2l3b1a',
            'data':'Trie 2, level 3, branch 1, child a'
        }
    )
    t2obj.add_nodes(
        {
            'name':'t2l1.t2l2b1.t2l3b1b',
            'data':'Trie 2, level 3, branch 1, child b'
            }
    )
    t2obj.add_nodes(
        {
            'name':'t2l1.t2l2b1.t2l3b1c',
            'data':'Trie 2, level 3, branch 1, child c'
        }
    )
    t2obj.add_nodes({'name':'t2l1', 'data':'Trie 2, level 1'})
    t2obj.add_nodes({'name':'t2l1.t2l2b1', 'data':'Trie 2, level 2, branch 1'})
    t2obj.add_nodes([
        {
            'name':'t2l1.t2l2b2.t2l3b2a',
            'data':'Trie 2, level 3, branch 2, child a'
        },
        {
            'name':'t2l1.t2l2b2.t2l3b2b',
            'data':'Trie 2, level 3, branch 2, child b'
        },
        {
            'name':'t2l1.t2l2b2.t2l3b2c',
            'data':'Trie 2, level 3, branch 2, child c'
        },
    ])
    t2obj.add_nodes({'name':'t2l1.t2l2b2', 'data':'Trie 2, level 2, branch 2'})
    ###
    t3obj = ptrie.Trie()
    t3obj.add_nodes([
        {'name':'t3l1', 'data':'Trie 3, level 1'},
        {'name':'t3l1.t3l2', 'data':'Trie 2, level 2'}
    ])
    t3obj.delete_subtree('t3l1.t3l2')
    ###
    t4obj = ptrie.Trie()
    t4obj.add_nodes([
        {'name':'root.branch1', 'data':5},
        {'name':'root.branch1', 'data':7},
        {'name':'root.branch2', 'data':[]},
        {'name':'root.branch1.leaf1', 'data':[]},
        {'name':'root.branch1.leaf1.subleaf1', 'data':333},
        {'name':'root.branch1.leaf2', 'data':'Hello world!'},
        {'name':'root.branch1.leaf2.subleaf2', 'data':[]},
    ])
    ###
    return t1obj, t2obj, t3obj, t4obj


###
# Test classes
###
class TestTrieNode(object):
    """ Tests for CsvFile class """
    ### Private methods
    def test_find_common_prefix(self):
        """ Test _find_common_prefix method behavior """
        tobj = ptrie.Trie('/')
        assert tobj._find_common_prefix(
            'root/hello/world',
            'root/hello'
        ) == 'root/hello'
        assert tobj._find_common_prefix('root/hello/world', 'root') == 'root'
        assert tobj._find_common_prefix('root/hello/world', 'branch') == ''

    def test_get_children_private(self, default_trees):
        """ Test _get_children method behavior """
        tree1, _, _, _ = default_trees
        assert sorted(tree1._get_children('t1l1')) == sorted(
            ['t1l1.t1l2b1', 't1l1.t1l2b2']
        )
        assert tree1._get_children('t1l1.t1l2b2.t1l3b2c') == []

    def test_get_data_private(self, default_trees):
        """ Test _get_data method behavior """
        _, _, _, tree4 = default_trees
        assert tree4._get_data('root.branch1.leaf1') == []
        assert tree4._get_data('root.branch1') == [5, 7]

    def test_get_parent_private(self, default_trees):
        """ Test _get_parent method behavior """
        tree1, _, _, _ = default_trees
        assert tree1._get_parent('t1l1') == ''
        assert tree1._get_parent('t1l1.t1l2b2.t1l3b2c') == 't1l1.t1l2b2'

    def test_set_children_private(self, default_trees):
        """ Test _set_children method behavior """
        _, _, _, tree4 = default_trees
        tree4._set_children(
            'root.branch1.leaf2',
            [
                'root.branch1.leaf2.c',
                'root.branch1.leaf2.x',
                'root.branch1.leaf2.a'
            ]
        )
        assert tree4._get_children('root.branch1.leaf2') == [
            'root.branch1.leaf2.a',
            'root.branch1.leaf2.c',
            'root.branch1.leaf2.x'
        ]

    def test_set_data_private(self, default_trees):
        """ Test _set_data method behavior """
        _, _, _, tree4 = default_trees
        tree4._set_data('root.branch1', ['Hello world'])
        assert tree4._get_data('root.branch1') == ['Hello world']

    def test_set_parent_private(self, default_trees):
        """ Test _set_parent method behavior """
        _, _, _, tree4 = default_trees
        tree4._set_parent('root.branch1.leaf2.subleaf2', 'leaf_zzz')
        assert tree4._get_parent('root.branch1.leaf2.subleaf2') == 'leaf_zzz'

    def test_validate_nodes_with_data(self):
        """ Test validate_nodes_with_data function """
        obj = ptrie.Trie()
        items = [
            {'name':'a.b.c', 'data':'a'},
            [{'name':'a.b', 'data':3}, {'name':'a.b.c', 'data':'a'}]
        ]
        for item in items:
            obj._validate_nodes_with_data(item)

    def test_validate_nodes_with_data_exceptions(self):
        """ Test _validate_nodes_with_data function exceptions """
        obj = ptrie.Trie()
        items = [
            [],
            3,
            [set(('name', 'hello')),
            {'name':5, 'data':'a'}],
            {'name':5, 'data':'a'},
            {'name':'a. b', 'data':None},
            {'name':'a.b..c', 'data':1.0}
        ]
        for item in items:
            AI(obj._validate_nodes_with_data, 'nodes', names=item)

    ### "Magic" methods
    def test_copy(self, default_trees):
        """ Test __copy__ method behavior """
        _, _, _, tree4 = default_trees
        ntree = copy.copy(tree4)
        assert id(ntree) != id(tree4)
        assert (ntree._db == tree4._db) and (id(ntree._db) != id(tree4._db))
        assert ntree._root == tree4._root
        assert ntree._root_hierarchy_length is tree4._root_hierarchy_length

    def test_str(self, default_trees):
        """ Test __str__ method behavior """
        tree1, tree2, tree3, _ = default_trees
        tree1.add_nodes([
            {'name':'t1l1.t1l2b1.t1l3b1a.leaf1', 'data':[]},
            {'name':'t1l1.t1l2b1.t1l3b1c.leaf2', 'data':[]},
            {'name':'t1l1.t1l2b1.t1l3b1c.leaf2.leaf3', 'data':[]},
            {'name':'t1l1.t1l2b1.t1l3b1c.leaf2.leaf3', 'data':[]},
            {'name':'t1l1.t1l2b1.t1l3b1c.leaf2.subleaf4', 'data':[]}
        ])
        assert str(tree1) == (
            't1l1 (*)\n'
            '├t1l2b1 (*)\n'
            '│├t1l3b1a (*)\n'
            '││└leaf1\n'
            '│├t1l3b1b (*)\n'
            '│└t1l3b1c (*)\n'
            '│ └leaf2\n'
            '│  ├leaf3\n'
            '│  └subleaf4\n'
            '└t1l2b2 (*)\n'
            ' ├t1l3b2a (*)\n'
            ' ├t1l3b2b (*)\n'
            ' └t1l3b2c (*)'
        )
        assert str(tree2) == (
            't2l1 (*)\n'
            '├t2l2b1 (*)\n'
            '│├t2l3b1a (*)\n'
            '│├t2l3b1b (*)\n'
            '│└t2l3b1c (*)\n'
            '└t2l2b2 (*)\n'
            ' ├t2l3b2a (*)\n'
            ' ├t2l3b2b (*)\n'
            ' └t2l3b2c (*)'
        )
        assert str(tree3) == 't3l1 (*)'
        tree3.add_nodes({'name':'t3l1.leaf1', 'data':[]})
        assert str(tree3) == 't3l1 (*)\n└leaf1'
        tree3.add_nodes({'name':'t3l1.leaf2', 'data':[]})
        assert str(tree3) == 't3l1 (*)\n├leaf1\n└leaf2'

    def test_nonzero(self):
        """ Test __nonzero__ method behavior """
        tobj = ptrie.Trie()
        assert not tobj
        tobj.add_nodes([{'name':'root.branch1', 'data':5}])
        assert tobj

    ### Public methods
    def test_add_nodes(self, default_trees):
        """ Test add_nodes method behavior """
        tree1, tree2, tree3, _ = default_trees
        assert tree1.get_children('t1l1') == ['t1l1.t1l2b1', 't1l1.t1l2b2']
        assert tree1.get_children('t1l1.t1l2b1') == [
            't1l1.t1l2b1.t1l3b1a',
            't1l1.t1l2b1.t1l3b1b',
            't1l1.t1l2b1.t1l3b1c'
        ]
        assert tree1.get_children('t1l1.t1l2b1.t1l3b1a') == []
        assert tree1.get_children('t1l1.t1l2b1.t1l3b1b') == []
        assert tree1.get_children('t1l1.t1l2b1.t1l3b1c') == []
        assert tree1.get_children('t1l1.t1l2b2') == [
            't1l1.t1l2b2.t1l3b2a',
            't1l1.t1l2b2.t1l3b2b',
            't1l1.t1l2b2.t1l3b2c'
        ]
        assert tree1.get_children('t1l1.t1l2b2.t1l3b2a') == []
        assert tree1.get_children('t1l1.t1l2b2.t1l3b2b') == []
        assert tree1.get_children('t1l1.t1l2b2.t1l3b2c') == []
        assert tree2.get_children('t2l1') == ['t2l1.t2l2b1', 't2l1.t2l2b2']
        assert tree2.get_children('t2l1.t2l2b1') == [
            't2l1.t2l2b1.t2l3b1a',
            't2l1.t2l2b1.t2l3b1b',
            't2l1.t2l2b1.t2l3b1c'
        ]
        assert tree2.get_children('t2l1.t2l2b1.t2l3b1a') == []
        assert tree2.get_children('t2l1.t2l2b1.t2l3b1b') == []
        assert tree2.get_children('t2l1.t2l2b1.t2l3b1c') == []
        assert tree2.get_children('t2l1.t2l2b2') == [
            't2l1.t2l2b2.t2l3b2a',
            't2l1.t2l2b2.t2l3b2b',
            't2l1.t2l2b2.t2l3b2c'
        ]
        assert tree2.get_children('t2l1.t2l2b2.t2l3b2a') == []
        assert tree2.get_children('t2l1.t2l2b2.t2l3b2b') == []
        assert tree2.get_children('t2l1.t2l2b2.t2l3b2c') == []
        assert tree3.get_children('t3l1') == []
        # Test that data id's are different
        tree4 = ptrie.Trie()
        ndata = [1, 2, 3]
        tree4.add_nodes([
            {'name':'root', 'data':[]},
            {'name':'root.leaf1', 'data':ndata},
            {'name':'root.leaf2', 'data':ndata}
        ])
        assert (
            id(tree4.get_data('root.leaf1'))
            !=
            id(tree4.get_data('root.leaf2'))
        )

    def test_add_nodes_exceptions(self):
        """ Test that add_nodes method exceptions """
        items = [
            5,
            {'key':'a'},
            {'name':'a'},
            {'data':'a'},
            {'name':'a.b', 'data':'a', 'edata':5},
            [{'name':'a.c', 'data':'a'}, {'key':'a'}],
            [{'name':'a.c', 'data':'a'}, {'name':'a'}],
            [{'name':'a.c', 'data':'a'}, {'data':'a'}],
            [
                {'name':'a.c', 'data':'a'},
                {'name':'a.b', 'data':'a', 'edata':5}
            ]
        ]
        for item in items:
            AI(ptrie.Trie().add_nodes, 'nodes', nodes=item)
        nodes = [{'name':'a.c', 'data':'a'}, {'name':'d.e', 'data':'a'}]
        exmsg = 'Illegal node name: d.e'
        AE(ptrie.Trie().add_nodes, ValueError, exmsg, nodes=nodes)

    def test_collapse_subtree(self):
        """ Test collapse_subtree method behavior """
        def create_tree():
            """ Create auxiliary tree for testing of recursive argument """
            tobj = ptrie.Trie('/')
            tobj.add_nodes([
                {'name':'hello/world/root', 'data':[]},
                {'name':'hello/world/root/anode', 'data':7},
                {'name':'hello/world/root/bnode', 'data':[]},
                {'name':'hello/world/root/cnode', 'data':[]},
                {'name':'hello/world/root/bnode/anode', 'data':[]},
                {'name':'hello/world/root/cnode/anode/leaf', 'data':[]}
            ])
            return tobj
        t1obj = ptrie.Trie()
        t1obj.add_nodes([
            {'name':'l0.l1', 'data':'hello'},
            {'name':'l0.l1.l2.l3b2.l4b2b1', 'data':5},
            {'name':'l0.l1.l2.l3b2.l4b2b1.l5b2b1b1', 'data':[]},
            {'name':'l0.l1.l2.l3b1.l4b1b1.l5b1b1b1.l6b1b1b1b1', 'data':[]},
            {'name':'l0.l1.l2.l3b1.l4b1b1.l5b1b1b1.l6b1b1b1b2', 'data':[]},
            {
                'name':'l0.l1.l2.l3b1.l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1',
                'data':[]
            },
        ])
        # Original tree       Collapsed tree
        # l0                  l0.l1 (*)
        # └l1 (*)             └l2
        #  └l2                 ├l3b1
        #   ├l3b1              │├l4b1b1.l5b1b1b1
        #   │├l4b1b1           ││├l6b1b1b1b1
        #   ││└l5b1b1b1        ││└l6b1b1b1b2
        #   ││ ├l6b1b1b1b1     │└l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1
        #   ││ └l6b1b1b1b2     └l3b2.l4b2b1 (*)
        #   │└l5b1b1            └l5b2b1b1
        #   │ └l5b1b1b2
        #   │  └l6b1b1b2b1
        #   │   └l7b1b1b2b1b1
        #   └l3b2
        #    └l4b2b1 (*)
        #     └l5b2b1b1
        t1obj.collapse_subtree(t1obj.root_name)
        assert str(t1obj) == (
            'l0.l1 (*)\n'
            '└l2\n'
            ' ├l3b1\n'
            ' │├l4b1b1.l5b1b1b1\n'
            ' ││├l6b1b1b1b1\n'
            ' ││└l6b1b1b1b2\n'
            ' │└l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1\n'
            ' └l3b2.l4b2b1 (*)\n'
            '  └l5b2b1b1'
        )
        assert t1obj.get_data('l0.l1') == ['hello']
        assert t1obj.get_data('l0.l1.l2.l3b2.l4b2b1') == [5]
        tobj = create_tree()
        tobj.collapse_subtree(tobj.root_name, False)
        assert str(tobj) == (
            'hello/world/root\n'
            '├anode (*)\n'
            '├bnode\n'
            '│└anode\n'
            '└cnode\n'
            ' └anode\n'
            '  └leaf'
        )
        tobj = create_tree()
        tobj.collapse_subtree(tobj.root_name, True)
        assert str(tobj) == (
            'hello/world/root\n'
            '├anode (*)\n'
            '├bnode/anode\n'
            '└cnode/anode/leaf'
        )

    def test_collapse_exceptions(self):
        """ Test collapse method exceptions """
        t1obj = ptrie.Trie('/')
        t1obj.add_nodes([{'name':'hello/world/root', 'data':[]}])
        name = t1obj.root_name
        AI(t1obj.collapse_subtree, 'recursive', name=name, recursive=5)

    def test_copy_subtree(self, default_trees):
        """ Test copy_subtree method behavior """
        _, _, _, tree4 = default_trees
        tree4.copy_subtree('root.branch1', 'root.branch2.branch3')
        # Original tree   Copied sub-tree
        # root            root
        # ├branch1 (*)    ├branch1 (*)
        # │├leaf1         │├leaf1
        # ││└subleaf1 (*) ││└subleaf1 (*)
        # │└leaf2 (*)     │└leaf2 (*)
        # │ └subleaf2     │ └subleaf2
        # └branch2        └branch2
        #                  └branch3 (*)
        #                   ├leaf1
        #                   │└subleaf1 (*)
        #                   └leaf2 (*)
        #                    └subleaf2
        # Test tree relationship
        assert str(tree4) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1\n'
            '││└subleaf1 (*)\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2\n'
            ' └branch3 (*)\n'
            '  ├leaf1\n'
            '  │└subleaf1 (*)\n'
            '  └leaf2 (*)\n'
            '   └subleaf2'
        )
        # Test that there are no pointers between source and destination data
        assert (id(tree4.get_data('root.branch1')) !=
               id(tree4.get_data('root.branch2.branch3')))
        assert (id(tree4.get_data('root.branch1.leaf1')) !=
               id(tree4.get_data('root.branch2.branch3.leaf1')))
        assert (id(tree4.get_data('root.branch1.leaf1.subleaf1')) !=
               id(tree4.get_data('root.branch2.branch3.leaf1.subleaf1')))
        assert (id(tree4.get_data('root.branch1.leaf2')) !=
               id(tree4.get_data('root.branch2.branch3.leaf2')))
        assert (id(tree4.get_data('root.branch1.leaf2.subleaf2')) !=
               id(tree4.get_data('root.branch2.branch3.leaf2.subleaf2')))
        # Test that data values are the same
        assert (tree4.get_data('root.branch1') ==
               tree4.get_data('root.branch2.branch3'))
        assert (tree4.get_data('root.branch1.leaf1') ==
               tree4.get_data('root.branch2.branch3.leaf1'))
        assert (tree4.get_data('root.branch1.leaf1.subleaf1') ==
               tree4.get_data('root.branch2.branch3.leaf1.subleaf1'))
        assert (tree4.get_data('root.branch1.leaf2') ==
               tree4.get_data('root.branch2.branch3.leaf2'))
        assert (tree4.get_data('root.branch1.leaf2.subleaf2') ==
               tree4.get_data('root.branch2.branch3.leaf2.subleaf2'))

    def test_copy_subtree_exceptions(self):
        """ Test copy_subtree method exceptions """
        obj = ptrie.Trie()
        obj.add_nodes([
            {'name':'root', 'data':[]},
            {'name':'root.leaf1', 'data':5},
            {'name':'root.leaf2', 'data':7}
        ])
        items = [5, '.x.y']
        dnode = 'root.x'
        fobj = obj.copy_subtree
        for item in items:
            AI(fobj, 'source_node', source_node=item, dest_node=dnode)
        exmsg = 'Node hello not in tree'
        AE(fobj, RE, exmsg, source_node='hello', dest_node=dnode)
        items = [5, 'x..y']
        for item in items:
            AI(fobj, 'dest_node', source_node='root.leaf1', dest_node=item)
        exmsg = 'Illegal root in destination node'
        AE(fobj, RE, exmsg, source_node='root.leaf1', dest_node='teto.leaf2')

    def test_delete_prefix(self):
        """ Test delete_prefix method behavior """
        tobj = ptrie.Trie('/')
        tobj.add_nodes(
            [
                {'name':'hello/world/root', 'data':[]},
                {'name':'hello/world/root/anode', 'data':7},
                {'name':'hello/world/root/bnode', 'data':[]},
                {'name':'hello/world/root/cnode', 'data':[]},
                {'name':'hello/world/root/bnode/anode', 'data':[]},
                {'name':'hello/world/root/cnode/anode/leaf', 'data':[]}
            ]
        )
        tobj.collapse_subtree(tobj.root_name, recursive=False)
        tobj.delete_prefix('hello/world')
        assert str(tobj) == (
            'root\n'
            '├anode (*)\n'
            '├bnode\n'
            '│└anode\n'
            '└cnode\n'
            ' └anode\n'
            '  └leaf'
        )

    def test_delete_prefix_exceptions(self):
        """ Test delete_prefix method exceptions """
        tobj = ptrie.Trie('/')
        tobj.add_nodes(
            [
                {'name':'hello/world/root', 'data':[]},
                {'name':'hello/world/root/anode', 'data':7},
                {'name':'hello/world/root/bnode', 'data':[]},
                {'name':'hello/world/root/cnode', 'data':[]},
                {'name':'hello/world/root/bnode/anode', 'data':[]},
                {'name':'hello/world/root/cnode/anode/leaf', 'data':[]}
            ]
        )
        AI(tobj.delete_prefix, 'name', name=5)
        items = ['hello/world/root', 'hello/world!!!!']
        exmsg = 'Argument `name` is not a valid prefix'
        for item in items:
            AE(tobj.delete_prefix, RE, exmsg, name=item)

    def test_delete_subtree(self, default_trees):
        """ Test delete_subtree method behavior """
        tree1, tree2, _, _ = default_trees
        tree1.delete_subtree('t1l1.t1l2b2')
        tree1.delete_subtree('t1l1.t1l2b1.t1l3b1b')
        tree2.delete_subtree('t2l1')
        assert str(tree1) == (
            't1l1 (*)\n'
            '└t1l2b1 (*)\n'
            ' ├t1l3b1a (*)\n'
            ' └t1l3b1c (*)'
        )
        assert str(tree2) == ''
        assert tree2.root_name is None
        tree2.add_nodes(
            [
                {'name':'root.branch1', 'data':[]},
                {'name':'root.branch1.x', 'data':1999}
            ]
        )
        assert tree2.root_name == 'root'

    def test_delete_subtree_exceptions(self, default_trees):
        """ Test delete_subtree method exceptions """
        tree1, _, _, _ = default_trees
        items = ['a..b', ['t1l1', 'a..b'], 5, ['t1l1', 5]]
        for item in items:
            AI(tree1.delete_subtree, 'nodes', nodes=item)
        exmsg = 'Node a.b.c not in tree'
        AE(tree1.delete_subtree, RE, exmsg, nodes='a.b.c')
        AE(tree1.delete_subtree, RE, exmsg, nodes=['t1l1', 'a.b.c'])

    def test_flatten_subtree(self, default_trees):
        """ Test flatten_subtree method behavior """
        _, _, _, tree4 = default_trees
        tree4.add_nodes(
            [
                {'name':'root.branch1.leaf1.subleaf2', 'data':[]},
                {'name':'root.branch2.leaf1', 'data':'loren ipsum'},
                {'name':'root.branch2.leaf1.another_subleaf1', 'data':[]},
                {'name':'root.branch2.leaf1.another_subleaf2', 'data':[]}
            ]
        )
        odata = copy.deepcopy(tree4.get_data('root.branch1.leaf1.subleaf1'))
        tree4.flatten_subtree('root.branch1.leaf1')
        assert str(tree4) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1.subleaf1 (*)\n'
            '│├leaf1.subleaf2\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2\n'
            ' └leaf1 (*)\n'
            '  ├another_subleaf1\n'
            '  └another_subleaf2'
        )
        assert tree4.get_data('root.branch1.leaf1.subleaf1') == odata
        tree4.flatten_subtree('root.branch2.leaf1')
        assert str(tree4) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1.subleaf1 (*)\n'
            '│├leaf1.subleaf2\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2\n'
            ' └leaf1 (*)\n'
            '  ├another_subleaf1\n'
            '  └another_subleaf2'
        )

    def test_get_children(self, default_trees):
        """ Test get_children method behavior """
        tree1, _, _, _ = default_trees
        assert tree1.get_children('t1l1') == ['t1l1.t1l2b1', 't1l1.t1l2b2']
        assert tree1.get_children('t1l1.t1l2b1') == [
            't1l1.t1l2b1.t1l3b1a',
            't1l1.t1l2b1.t1l3b1b',
            't1l1.t1l2b1.t1l3b1c'
        ]
        assert tree1.get_children('t1l1.t1l2b2') == [
            't1l1.t1l2b2.t1l3b2a',
            't1l1.t1l2b2.t1l3b2b',
            't1l1.t1l2b2.t1l3b2c'
        ]
        assert tree1.get_children('t1l1.t1l2b1.t1l3b1a') == []
        assert tree1.get_children('t1l1.t1l2b1.t1l3b1b') == []
        assert tree1.get_children('t1l1.t1l2b1.t1l3b1c') == []
        assert tree1.get_children('t1l1.t1l2b2.t1l3b2a') == []
        assert tree1.get_children('t1l1.t1l2b2.t1l3b2b') == []
        assert tree1.get_children('t1l1.t1l2b2.t1l3b2c') == []

    def test_get_data(self, default_trees):
        """ Test get_data method behavior """
        tree1, tree2, tree3, _ = default_trees
        assert tree1.get_data('t1l1') == ['Trie 1, level 1']
        assert tree1.get_data('t1l1.t1l2b1') == ['Trie 1, level 2, branch 1']
        assert tree1.get_data('t1l1.t1l2b1.t1l3b1a') == [
            'Trie 1, level 3, branch 1, child a'
        ]
        assert tree1.get_data('t1l1.t1l2b1.t1l3b1b') == [
            'Trie 1, level 3, branch 1, child b'
        ]
        assert tree1.get_data('t1l1.t1l2b1.t1l3b1c') == [
            'Trie 1, level 3, branch 1, child c']
        assert tree1.get_data('t1l1.t1l2b2') == ['Trie 1, level 2, branch 2'
                                           ]
        assert tree1.get_data('t1l1.t1l2b2.t1l3b2a') == [
            'Trie 1, level 3, branch 2, child a']
        assert tree1.get_data('t1l1.t1l2b2.t1l3b2b') == [
            'Trie 1, level 3, branch 2, child b'
        ]
        assert tree1.get_data('t1l1.t1l2b2.t1l3b2c') == [
            'Trie 1, level 3, branch 2, child c'
        ]
        assert tree2.get_data('t2l1') == ['Trie 2, level 1']
        assert tree2.get_data('t2l1.t2l2b1') == ['Trie 2, level 2, branch 1']
        assert tree2.get_data('t2l1.t2l2b1.t2l3b1a') == [
            'Trie 2, level 3, branch 1, child a'
        ]
        assert tree2.get_data('t2l1.t2l2b1.t2l3b1b') == [
            'Trie 2, level 3, branch 1, child b'
        ]
        assert tree2.get_data('t2l1.t2l2b1.t2l3b1c') == [
            'Trie 2, level 3, branch 1, child c']
        assert tree2.get_data('t2l1.t2l2b2') == ['Trie 2, level 2, branch 2'
                                           ]
        assert tree2.get_data('t2l1.t2l2b2.t2l3b2a') == [
            'Trie 2, level 3, branch 2, child a'
        ]
        assert tree2.get_data('t2l1.t2l2b2.t2l3b2b') == [
            'Trie 2, level 3, branch 2, child b'
        ]
        assert tree2.get_data('t2l1.t2l2b2.t2l3b2c') == [
            'Trie 2, level 3, branch 2, child c'
        ]
        assert tree3.get_data('t3l1') == ['Trie 3, level 1']
        tree4 = ptrie.Trie()
        tree4.add_nodes({'name':'t4l1', 'data':[]})
        assert tree4.get_data('t4l1') == []
        tree4.add_nodes([
            {'name':'t4l1', 'data':'Hello'},
            {'name':'t4l1', 'data':'world'}
        ])
        tree4.add_nodes({'name':'t4l1', 'data':'!'})
        assert tree4.get_data('t4l1') == ['Hello', 'world', '!']

    def test_get_leafs(self, default_trees):
        """ Test get_leafs method behavior """
        tree1, tree2, tree3, tree4 = default_trees
        assert tree1.get_leafs('t1l1') == [
            't1l1.t1l2b1.t1l3b1a',
            't1l1.t1l2b1.t1l3b1b',
            't1l1.t1l2b1.t1l3b1c',
            't1l1.t1l2b2.t1l3b2a',
            't1l1.t1l2b2.t1l3b2b',
            't1l1.t1l2b2.t1l3b2c'
        ]
        assert tree2.get_leafs('t2l1.t2l2b2') == [
            't2l1.t2l2b2.t2l3b2a',
            't2l1.t2l2b2.t2l3b2b',
            't2l1.t2l2b2.t2l3b2c'
        ]
        assert tree3.get_leafs('t3l1') == ['t3l1']
        assert tree4.get_leafs('root.branch1.leaf2') == [
            'root.branch1.leaf2.subleaf2'
        ]

    def test_get_node(self, default_trees):
        """ Test get_node method behavior """
        tree1, _, _, _ = default_trees
        assert tree1.get_node('t1l1') == {
            'parent':'',
            'children':['t1l1.t1l2b1', 't1l1.t1l2b2'],
            'data':['Trie 1, level 1']
        }
        assert tree1.get_node('t1l1.t1l2b1') == {
            'parent':'t1l1',
            'children':[
                't1l1.t1l2b1.t1l3b1a',
                't1l1.t1l2b1.t1l3b1b',
                't1l1.t1l2b1.t1l3b1c'
            ],
            'data':['Trie 1, level 2, branch 1']
        }
        assert tree1.get_node('t1l1.t1l2b1.t1l3b1a') == {
            'parent':'t1l1.t1l2b1',
            'children':[],
            'data':['Trie 1, level 3, branch 1, child a']
        }

    def test_get_node_children(self, default_trees):
        """ Test get_node_children method behavior """
        tree1, _, tree3, tree4 = default_trees
        assert tree1.get_node_children('t1l1') == [
            {
                'parent':'t1l1',
                'children':[
                    't1l1.t1l2b1.t1l3b1a',
                    't1l1.t1l2b1.t1l3b1b',
                    't1l1.t1l2b1.t1l3b1c'
                ],
                'data':['Trie 1, level 2, branch 1']
            },
            {
                'parent':'t1l1',
                'children':[
                    't1l1.t1l2b2.t1l3b2a',
                    't1l1.t1l2b2.t1l3b2b',
                    't1l1.t1l2b2.t1l3b2c'
                ],
                'data':['Trie 1, level 2, branch 2']
            }
        ]
        assert tree3.get_node_children('t3l1') == []
        assert tree4.get_node_children('root.branch1.leaf2') == [
            {'parent':'root.branch1.leaf2', 'children':[], 'data':[]}
        ]

    def test_get_node_parent(self, default_trees):
        """ Test get_node_parent method behavior """
        tree1, _, _, _ = default_trees
        assert tree1.get_node_parent('t1l1') == dict()
        assert tree1.get_node_parent('t1l1.t1l2b1') == {
            'parent':'',
            'children':['t1l1.t1l2b1', 't1l1.t1l2b2'],
            'data':['Trie 1, level 1']
        }

    def test_get_subtree(self, default_trees):
        """ Test get_subtree method behavior """
        _, _, tree3, tree4 = default_trees
        assert tree4.get_subtree('root.branch1') == [
            'root.branch1',
            'root.branch1.leaf1',
            'root.branch1.leaf1.subleaf1',
            'root.branch1.leaf2',
            'root.branch1.leaf2.subleaf2'
        ]
        assert tree3.get_subtree('t3l1') == ['t3l1']

    def test_in_tree(self, default_trees):
        """ Test in_tree method behavior """
        tree1, _, _, _ = default_trees
        assert not tree1.in_tree('x.x.x')
        assert tree1.in_tree('t1l1.t1l2b1')

    def test_in_tree_exceptions(self, default_trees):
        """ Test in_tree method exceptions """
        tree1, _, _, _ = default_trees
        items = ['a..b', 5]
        for item in items:
            AI(tree1.in_tree, 'name', name=item)

    def test_is_leaf(self, default_trees):
        """ Test is_leaf property behavior """
        tree1, tree2, tree3, _ = default_trees
        assert not tree1.is_leaf('t1l1')
        assert not tree2.is_leaf('t2l1.t2l2b1')
        assert tree2.is_leaf('t2l1.t2l2b1.t2l3b1b')
        assert tree3.is_leaf('t3l1')

    def test_is_root(self, default_trees):
        """ Test is_root property behavior """
        tree1, tree2, tree3, _ = default_trees
        assert tree1.is_root('t1l1')
        assert not tree2.is_root('t2l1.t2l2b1')
        assert not tree2.is_root('t2l1.t2l2b1.t2l3b1b')
        assert tree3.is_root('t3l1')

    def test_make_root(self, default_trees):
        """ Test make_root method behavior """
        #   Original tree       Make root tree
        #   root                root.branch1 (*)
        #   ├branch1 (*)        ├leaf1
        #   │├leaf1             │└subleaf1 (*)
        #   ││└subleaf1 (*)     └leaf2 (*)
        #   │└leaf2 (*)          └subleaf2
        #   │ └subleaf2
        #   └branch2
        _, _, _, tree4 = default_trees
        tree4.make_root('root')
        assert str(tree4) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1\n'
            '││└subleaf1 (*)\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2'
        )
        tree4.make_root('root.branch1')
        assert str(tree4) == (
            'root.branch1 (*)\n'
            '├leaf1\n'
            '│└subleaf1 (*)\n'
            '└leaf2 (*)\n'
            ' └subleaf2'
        )
        tree4.make_root('root.branch1.leaf2.subleaf2')
        assert str(tree4) == 'root.branch1.leaf2.subleaf2'

    def test_print_node(self, default_trees):
        """ Test print_node method behavior """
        tree1, tree2, tree3, _ = default_trees
        obj = ptrie.Trie()
        obj.add_nodes([
            {'name':'dtree', 'data':[]},
            {'name':'dtree.my_child', 'data':'Trie 2, level 2'}
        ])
        #
        assert tree1.print_node('t1l1') == (
            'Name: t1l1\n'
            'Parent: None\n'
            'Children: t1l2b1, t1l2b2\n'
            'Data: Trie 1, level 1'
        )
        tree2.add_nodes({'name':'t2l1.t2l2b1.t2l3b1b', 'data':14})
        assert tree2.print_node('t2l1.t2l2b1.t2l3b1b') == (
            "Name: t2l1.t2l2b1.t2l3b1b\n"
            "Parent: t2l1.t2l2b1\n"
            "Children: None\n"
            "Data: ['Trie 2, level 3, branch 1, child b', 14]"
        )
        assert tree3.print_node('t3l1') == (
            'Name: t3l1\n'
            'Parent: None\n'
            'Children: None\n'
            'Data: Trie 3, level 1'
        )
        assert obj.print_node('dtree') == (
            'Name: dtree\n'
            'Parent: None\n'
            'Children: my_child\n'
            'Data: None'
        )

    def test_rename_node(self, default_trees):
        """ Test rename_node method behavior """
        _, _, _, tree4 = default_trees
        tree4.rename_node('root.branch1.leaf1', 'root.branch1.mapleleaf1')
        assert str(tree4) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf2 (*)\n'
            '││└subleaf2\n'
            '│└mapleleaf1\n'
            '│ └subleaf1 (*)\n'
            '└branch2'
        )
        tree4.rename_node('root', 'dummy')
        assert str(tree4) == (
            'dummy\n'
            '├branch1 (*)\n'
            '│├leaf2 (*)\n'
            '││└subleaf2\n'
            '│└mapleleaf1\n'
            '│ └subleaf1 (*)\n'
            '└branch2'
        )
        tobj = ptrie.Trie()
        root = 'dummy.levels.root.'
        tobj.add_nodes(
            [
                {'name':root+'branch1', 'data':[]},
                {'name':root+'branch2', 'data':[]},
                {'name':root+'branch1.leaf1', 'data':[]},
                {'name':root+'branch1.leaf1.subleaf1', 'data':333},
                {'name':root+'branch1.leaf2', 'data':'Hello world!'},
                {'name':root+'branch1.leaf2.subleaf2', 'data':[]},
            ]
        )
        tobj.make_root('dummy.levels.root')
        tobj.rename_node('dummy.levels.root', 'top')
        assert str(tobj) == (
            'top\n'
            '├branch1\n'
            '│├leaf1\n'
            '││└subleaf1 (*)\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2'
        )

    def test_rename_node_exceptions(self, default_trees):
        """ Test rename_node method exceptions """
        _, _, _, tree4 = default_trees
        items = [5, 'a.b..c']
        for item in items:
            AI(tree4.rename_node, 'name', name=item, new_name='root.x')
        exmsg = 'Node a.b.c not in tree'
        AE(tree4.rename_node, RE, exmsg, name='a.b.c', new_name='root.x')
        items = [5, 'a..b']
        for item in items:
            AI(tree4.rename_node, 'new_name', name='root', new_name=item)
        exmsg = 'Node root.branch1 already exists'
        root = 'root.branch1'
        AE(tree4.rename_node, RE, exmsg, name=root, new_name=root)
        exmsg = 'Argument `new_name` has an illegal root node'
        AE(tree4.rename_node, RE, exmsg, name=root, new_name='a.b.c')
        exmsg = 'Argument `new_name` is an illegal root node name'
        AE(tree4.rename_node, RE, exmsg, name='root', new_name='dummy.hier')

    def test_search_tree(self):
        """ Test search method behavior """
        tobj = ptrie.Trie('/')
        tobj.add_nodes(
            [
                {'name':'root', 'data':[]},
                {'name':'root/anode', 'data':[]},
                {'name':'root/bnode', 'data':[]},
                {'name':'root/cnode', 'data':[]},
                {'name':'root/bnode/anode', 'data':[]},
                {'name':'root/cnode/anode/leaf', 'data':[]},
                {'name':'root/cnode/anode/leaf1', 'data':[]}
            ]
        )
        assert tobj.search_tree('anode') == sorted(
            [
                'root/anode',
                'root/bnode/anode',
                'root/cnode/anode',
                'root/cnode/anode/leaf',
                'root/cnode/anode/leaf1'
            ]
        )
        assert tobj.search_tree('leaf') == sorted(['root/cnode/anode/leaf'])
        tobj = ptrie.Trie('/')
        tobj.add_nodes(
            [
                {'name':'anode', 'data':[]},
                {'name':'anode/some_node', 'data':[]}
            ]
        )
        assert (
            tobj.search_tree('anode') == sorted(['anode', 'anode/some_node'])
        )
        tobj = ptrie.Trie('/')
        tobj.add_nodes({'name':'anode', 'data':[]})
        assert tobj.search_tree('anode') == sorted(['anode'])

    def test_search_tree_exceptions(self):
        """ Test search method exceptions """
        tobj = ptrie.Trie('/')
        tobj.add_nodes(
            [
                {'name':'root', 'data':[]},
                {'name':'root/anode', 'data':[]},
                {'name':'root/bnode', 'data':[]},
                {'name':'root/cnode', 'data':[]},
                {'name':'root/bnode/anode', 'data':[]},
                {'name':'root/cnode/anode/leaf', 'data':[]},
                {'name':'root/cnode/anode/leaf1', 'data':[]}
            ]
        )
        items = [5, 'a/ b', 'a/b//c']
        for item in items:
            AI(tobj.search_tree, 'name', name=item)

    ### Properties
    def test_node_separator(self, default_trees):
        """ Test node_separator property """
        def create_tree():
            """ Create test tree """
            tobj = ptrie.Trie('+')
            tobj.add_nodes(
                [
                    {'name':'root+branch1', 'data':5},
                    {'name':'root+branch1', 'data':7},
                    {'name':'root+branch2', 'data':[]},
                    {'name':'root+branch1+leaf1', 'data':[]},
                    {'name':'root+branch1+leaf1+subleaf1', 'data':333},
                    {'name':'root+branch1+leaf2', 'data':'Hello world!'},
                    {'name':'root+branch1+leaf2+subleaf2', 'data':[]},
                ]
            )
            return tobj
        tobj = create_tree()
        assert str(tobj) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1\n'
            '││└subleaf1 (*)\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2'
        )
        tobj.collapse_subtree('root+branch1')
        assert str(tobj) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1+subleaf1 (*)\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2'
        )
        tobj = create_tree()
        tobj.copy_subtree('root+branch1', 'root+branch3')
        assert str(tobj) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1\n'
            '││└subleaf1 (*)\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '├branch2\n'
            '└branch3 (*)\n'
            ' ├leaf1\n'
            ' │└subleaf1 (*)\n'
            ' └leaf2 (*)\n'
            '  └subleaf2'
        )
        tobj = create_tree()
        tobj.delete_subtree(['root+branch1+leaf1', 'root+branch2'])
        assert str(tobj) == (
            'root\n'
            '└branch1 (*)\n'
            ' └leaf2 (*)\n'
            '  └subleaf2'
        )
        tobj = create_tree()
        tobj.add_nodes(
            [
                {'name':'root+branch1+leaf1+subleaf2', 'data':[]},
                {'name':'root+branch2+leaf1', 'data':'loren ipsum'},
                {'name':'root+branch2+leaf1+another_subleaf1', 'data':[]},
                {'name':'root+branch2+leaf1+another_subleaf2', 'data':[]}
            ]
        )
        tobj.flatten_subtree('root+branch1+leaf1')
        assert str(tobj) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1+subleaf1 (*)\n'
            '│├leaf1+subleaf2\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2\n'
            ' └leaf1 (*)\n'
            '  ├another_subleaf1\n'
            '  └another_subleaf2'
        )
        tobj.flatten_subtree('root+branch2+leaf1')
        assert str(tobj) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf1+subleaf1 (*)\n'
            '│├leaf1+subleaf2\n'
            '│└leaf2 (*)\n'
            '│ └subleaf2\n'
            '└branch2\n'
            ' └leaf1 (*)\n'
            '  ├another_subleaf1\n'
            '  └another_subleaf2'
        )
        tobj = create_tree()
        assert sorted(tobj.get_subtree('root+branch1')) == sorted(
            [
                'root+branch1',
                'root+branch1+leaf1',
                'root+branch1+leaf1+subleaf1',
                'root+branch1+leaf2',
                'root+branch1+leaf2+subleaf2'
            ]
        )
        tobj = create_tree()
        tobj.make_root('root+branch1')
        assert str(tobj) == (
            'root+branch1 (*)\n'
            '├leaf1\n'
            '│└subleaf1 (*)\n'
            '└leaf2 (*)\n'
            ' └subleaf2'
        )
        tobj = create_tree()
        tobj.rename_node('root+branch1+leaf1', 'root+branch1+mapleleaf1')
        assert str(tobj) == (
            'root\n'
            '├branch1 (*)\n'
            '│├leaf2 (*)\n'
            '││└subleaf2\n'
            '│└mapleleaf1\n'
            '│ └subleaf1 (*)\n'
            '└branch2'
        )
        #
        tree1, _, _, _ = default_trees
        assert tree1.node_separator == '.'

    def test_node_separator_exceptions(self):
        """
        Check that validation for node_separator argument works as expected
        """
        items = [3, 'hello']
        for item in items:
            AI(ptrie.Trie, 'node_separator', node_separator=item)
        ptrie.Trie('+')

    def test_root_name(self, default_trees):
        """ Test root_name property behavior """
        tree1, _, _, _ = default_trees
        tree4 = ptrie.Trie()
        assert tree1.root_name == 't1l1'
        assert tree4.root_name is None

    def test_root_node(self, default_trees):
        """ Test root_node property behavior """
        tree1, _, _, _ = default_trees
        tree4 = ptrie.Trie()
        assert tree1.root_node == {
            'parent':'',
            'children':['t1l1.t1l2b1', 't1l1.t1l2b2'],
            'data':['Trie 1, level 1']
        }
        assert tree4.root_node is None

    def test_cannot_delete_attributes_exceptions(self, default_trees):
        """
        Test that del method raises an exception on all class attributes
        """
        tree1, _, _, _ = default_trees
        props = ['nodes', 'node_separator', 'root_name', 'root_node']
        for prop in props:
            AROPROP(tree1, prop)

    ### Miscellaneous
    def test_single_node_function_exceptions(self):
        """
        Check that correct exceptions are raise for methods that have a single
        NodeName argument that has to be in the tree
        """
        obj = ptrie.Trie()
        method_list = [
            'collapse_subtree', 'flatten_subtree', 'get_children', 'get_data',
            'get_leafs', 'get_node', 'get_node_children', 'get_node_parent',
            'get_subtree', 'is_leaf', 'is_root', 'is_leaf', 'make_root',
            'print_node'
        ]
        items = [5, 'a.b..c']
        for method in method_list:
            func = getattr(obj, method)
            for item in items:
                AI(func, 'name', name=item)
            AE(func, RE, 'Node a.b.c not in tree', name='a.b.c')
