# -*- coding: utf-8 -*-
import os
import pandas as pd

from output_funcs import to_csv, summarycsv, to_shps, get_summary_df, to_nx

class Output_Main(object):
    def __init__(self):
        self.mainobj = None
        self.nodes = None

    def update_obj(self, obj, namekey):
        if namekey=='mainobj':
            self.mainobj = obj
        elif namekey=='nodes':
            self.nodes = obj
        else:
            print 'something wrong, output object not update'
            print 'namekey'+namekey

    def get_nodedf(self, items):
        output_data = {}
        col_sort = ['node_id','xcor','ycor']
        for dic in items:
            cols = dic[dic.keys()[0]].keys()
            col_sort.extend(cols)
        #print col_sort
        for nn in self.nodes:
            xx,yy = self.nodes[nn]
            z = dict(node_id=nn, xcor=xx, ycor=yy)
            for dic in items:
                z.update(dic[nn])
            output_data[nn] = z
        output_df = pd.DataFrame.from_dict(output_data, orient='index')
        output_df = output_df[col_sort]
        return output_df

    def get_summary_df(self):
        sum_df = get_summary_df(self)
        return sum_df

    def summarycsv(self, filename=None):
        summarycsv(self, filename=filename)

    def to_csv(self, filename=None, items=[]):
        to_csv(self, filename=filename, items=items)

    def to_shps(self, filename_prefix=None, crs=None, items=[]):
        to_shps(self, filename_prefix=filename_prefix, crs=crs, items=items)

    def to_nx(self, items=[], pos_dic=True):
        ag,pos = to_nx(self, items=items)
        if pos_dic:
            return (ag,pos)
        else:
            return ag
