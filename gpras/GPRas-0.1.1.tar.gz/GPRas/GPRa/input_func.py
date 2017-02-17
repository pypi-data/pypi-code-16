# -*- coding: utf-8 -*-

from input_funcs import FileReading_csv, DataImport_nx

class Data_Set(object):
    def __init__(self):
        self.item = None

    def from_csv(self, nodefile, linkfile, node_filesetup=None, link_filesetup=None):
        self.item = FileReading_csv(nodefile, linkfile, node_filesetup=node_filesetup, link_filesetup=link_filesetup)

    def from_nx(self, agraph, node_setup=None, link_setup=None):
        ## for using nx.Graph as input
        self.item = DataImport_nx(agraph, node_setup=node_setup, link_setup=link_setup)
        
