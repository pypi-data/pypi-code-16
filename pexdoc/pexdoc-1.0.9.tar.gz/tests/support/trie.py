# trie.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0613


import ptrie

import pexdoc


def create_trie():
    """ Create trie and add exception """
    exobj = pexdoc.exh.get_or_create_exh_obj()
    exobj.add_exception(
        'invalid_node_separator',
        RuntimeError,
        'Argument `node_separator` is not valid'
    )
    return ptrie.Trie('.')

def add_nodes(tobj, nodes):
    """ Add nodes to trie """
    exobj = pexdoc.exh.get_or_create_exh_obj()
    exobj.add_exception(
        'illegal_node_name',
        ValueError,
        'Illegal node name: *[node_name]*'
    )
    tobj.add_nodes(nodes)
