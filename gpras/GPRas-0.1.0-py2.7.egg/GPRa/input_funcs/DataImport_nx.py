# -*- coding: utf-8 -*-
import math
import numpy
import networkx as nx

class DataImport_nx(object):
    def __init__(self, agraph, node_setup=None, link_setup=None):
        #self.nodefile = nodefile
        #self.linkfile = linkfile
        agraph = nx.Graph(agraph)
        self.nodes, self.nodes_loc = self.nodes(agraph, node_setup)
        self.loc_nodes = { v:k for k,v in self.nodes_loc.iteritems() }
        #print self.nodes
        self.nn = len(self.nodes)
        self.links, self.dmin, self.dmax = self.links(agraph, link_setup)
        self.matrix = self.ODmatrix()

    def nodes(self, agraph, node_fs):
        if node_fs is None:
            node_fs = {'xcor': 'xcor', 'ycor':'ycor'}
        else:
            if (not('xcor' in node_fs) or not('ycor' in node_fs)):
                raise NameError("'xcor' and 'ycor' keys must in node_filesetup dict")
        #node0 = []
        nodes = {}
        nodes_loc = {}
        gnodes = agraph.nodes
        i = 0
        for n,d in agraph.nodes_iter(data=True):
            xx = d[node_fs['xcor']]
            yy = d[node_fs['ycor']]
            nodes[n] = (xx,yy)
            nodes_loc[n] = i
            i+=1
        return nodes, nodes_loc

    def links(self, agraph, link_fs):
        if link_fs is None:
            link_fs = {'weight': None}
        else:
            if not ('weight' in link_fs):
                link_fs['weight'] = None
        link = []
        distlist = []
        for u,v,d in agraph.edges_iter(data=True):
            if not (link_fs['weight'] is None):
                w = d[link_fs['weight']]
            else:
                w = None
            link.append((u,v,w))
            distlist.append( self.distancebetween(u,v) )
        return link, min(distlist), max(distlist)

    def ODmatrix(self):
        # create OD-matrix
        nn = len(self.nodes)
        OD_time = numpy.zeros((nn,nn)) # 0,1 matrix
        for m in self.links:
            #print m
            o0, d0, w0 = m
            o = self.nodes_loc[o0]
            d = self.nodes_loc[d0]
            #o = int(o0) - 1
            #d = int(d0) - 1
            #w = float(w0)
            OD_time[o][d] = 1.0
            OD_time[d][o] = 1.0
        return OD_time

    def distancebetween(self,node1,node2):
        #print node1 in self.nodes.keys()
        #print node2 in self.nodes.keys()
        x1, y1 = self.nodes[node1]
        x2, y2 = self.nodes[node2]
        dist = float(math.sqrt((x1-x2)**2 + (y1-y2)**2))
        return dist
