# -*- coding: utf-8 -*-

import os
import pandas as pd

def to_csv(oo, filename=None, items=[]):
    if filename is None:
        filename = "temp_output/temp_result.csv"
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    output_df = oo.get_nodedf(items)
    output_df.to_csv(filename, index_label='ind')

def get_summary_df(oo):
    summary = {}
    alpha = oo.mainobj.alpha
    beta = oo.mainobj.beta
    gamma = oo.mainobj.gamma
    itertime = oo.mainobj.iteration
    dmin = oo.mainobj.dmin
    dmax = oo.mainobj.dmax
    nn = len(oo.mainobj.node)
    ll = len(oo.mainobj.link)
    ave_deg = sum(oo.mainobj.degree)/len(oo.mainobj.degree)
    net_dens = float(ll)/(float(nn*(nn-1))/2.)

    summary = dict(
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        iteration_time=itertime,
        dmin=dmin,
        dmax=dmax,
        no_node=nn,
        no_link=ll,
        ave_degree=ave_deg,
        network_density=net_dens,
    )

    summary_rows = ['alpha','beta','gamma','iteration_time','dmin','dmax','no_node','no_link','ave_degree','network_density']
    summary_df = pd.DataFrame.from_dict(summary, orient='index')
    summary_df.columns = ['value']
    summary_df = summary_df.reindex(summary_rows)
    #print summary_df
    return summary_df

def summarycsv(oo, filename=None):
    if filename is None:
        filename = "temp_output/temp_summary.csv"
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    summary_df = get_summary_df(oo)
    summary_df.to_csv(filename, index_label='name')
