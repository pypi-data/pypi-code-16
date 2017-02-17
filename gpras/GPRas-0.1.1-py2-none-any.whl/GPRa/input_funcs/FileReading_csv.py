# -*- coding: utf-8 -*-

"""
read files
"""
#import csv
import numpy
#import shapefile
import math
import pandas as pd

class FileReading_csv(object):
    def __init__(self, nodefile, linkfile, node_filesetup=None, link_filesetup=None):
        #self.nodefile = nodefile
        #self.linkfile = linkfile

        self.nodes, self.nodes_loc = self.nodes(nodefile, node_filesetup)
        self.loc_nodes = { v:k for k,v in self.nodes_loc.iteritems() }
        #print self.nodes
        self.nn = len(self.nodes)
        self.links, self.dmin, self.dmax = self.links(linkfile, link_filesetup)
        self.matrix = self.ODmatrix()

    def nodes(self, nodefile, node_fs):
        if node_fs is None:
            node_fs = {'node_id':'nid', 'xcor': 'xcor', 'ycor':'ycor'}
        else:
            if (not('node_id' in node_fs) or not('xcor' in node_fs) or not('ycor' in node_fs)):
                raise NameError("'node_id', 'xcor' and 'ycor' keys must in node_filesetup dict")
        #node0 = []
        nodes = {}
        nodes_loc = {}
        ndf = pd.read_csv(nodefile)
        nids = ndf[node_fs['node_id']].tolist()
        xcors = ndf[node_fs['xcor']].tolist()
        ycors = ndf[node_fs['ycor']].tolist()
        i = 0
        for nn,xx,yy in zip(nids,xcors,ycors):
            #node0.append((nn, xx, yy))
            nodes[nn] = (xx,yy)
            nodes_loc[nn] = i
            i+=1
        return nodes, nodes_loc

    def links(self, linkfile, link_fs):
        if link_fs is None:
            link_fs = {'ori':'ori','des':'des','weight':None}
        else:
            if (not('ori' in link_fs) or not('des' in link_fs)):
                raise NameError("'ori' and 'des' keys must in link_filesetup dict")
            if not ('weight' in link_fs):
                link_fs['weight'] = None
        link = []
        distlist = []
        ldf = pd.read_csv(linkfile)
        oris = ldf[link_fs['ori']].tolist()
        dess = ldf[link_fs['des']].tolist()
        weis = None
        if not  (link_fs['weight'] is None):
            weis = ldf[link_fs['weight']].tolist()
        else:
            weis = [None]*len(oris)
        for oo,dd,ww in zip(oris,dess,weis):
            link.append((oo,dd,ww))
            distlist.append( self.distancebetween(oo,dd) )
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
