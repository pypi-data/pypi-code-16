# -*- coding: utf-8 -*-

import networkx as nx

def to_nx(oo, items=[]):
    #nodes_df = oo.get_nodedf(items)
    nodes = oo.nodes
    links = oo.mainobj.link

    nodes_data = []
    for nn in nodes:
        xx,yy = nodes[nn]
        z = dict(node_id=nn, xcor=xx, ycor=yy)
        for dic in items:
            z.update(dic[nn])
        nodes_data.append((nn,z))

    ag = nx.Graph()
    ag.add_nodes_from(nodes_data)

    for u,v,w in links:
        ag.add_edge(u,v)

    pos = nodes
    return (ag,pos)
