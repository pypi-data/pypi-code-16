# -*- coding: utf-8 -*-

from GPRa import GPRs, Data_Set, Output_Main

class GPRas(object):
    def __init__(self):
        self.dataset = Data_Set()
        self.GPRa = GPRs()

        self.pr_dic = None
        self.wpr_dic = None
        self.ddpr_dic = None
        self.gpr_dic = None
        self.eddpr_dic = None
        self.egpr_dic = None

        self.oo = Output_Main()

    def Initialize(self, iteration=50000, alpha=1., beta=1., gamma=1.):
        ## self.dataset.from_csv(xxx) must be runned before concentration
        if self.dataset.item is None:
            raise NameError("dataset is not set yet")
        self.GPRa.initialize(self.dataset.item, iteration=iteration, alpha=alpha, beta=beta, gamma=gamma)
        self.oo.update_obj(self.dataset.item.nodes, 'nodes')
        self.oo.update_obj(self.GPRa, 'mainobj')

    def get_dict(self, score, rank, prefix=''):
        res_dict = {}
        loc_nodes = self.GPRa.loc_nodes
        k1 = prefix+'_'+'score'
        k2 = prefix+'_'+'rank'
        #print score[1,0]
        for i in range(len(score)):
            # location i == node_id nn
            ss = score[i,0]
            rr = rank[i,0]
            nn = loc_nodes[i]
            res_dict[nn] = {k1:ss, k2:rr}
            #print type(ss), ss
        return res_dict

    def CalculateAll(self):
        self.PR()
        self.WPR()
        self.DDPR()
        self.GPR()
        self.eDDPR()
        self.eGPR()

    def PR(self):
        pr = self.GPRa.PR(return_type="score")
        rpr = self.GPRa.PR_ranks()
        self.pr_dic = self.get_dict(pr,rpr, prefix='PR')

    def WPR(self, alpha=None, update=False):
        if update:
            self.GPRa.alpha = alpha
        wpr = self.GPRa.WPR(return_type="score", alpha=alpha, update=update)
        rwpr = self.GPRa.WPR_ranks()
        self.wpr_dic = self.get_dict(wpr,rwpr, prefix='WPR')

    def DDPR(self, beta=None, update=False):
        if update:
            self.GPRa.beta = beta
        ddpr = self.GPRa.DDPR(return_type="score", beta=beta, update=update)
        rddpr = self.GPRa.DDPR_ranks()
        self.ddpr_dic = self.get_dict(ddpr,rddpr, prefix='DDPR')

    def GPR(self, alpha=None, beta=None, update=False):
        if update:
            self.GPRa.alpha = alpha
            self.GPRa.beta = beta
        gpr = self.GPRa.GPR(return_type="score", alpha=alpha, beta=beta, update=update)
        rgpr = self.GPRa.GPR_ranks()
        self.gpr_dic = self.get_dict(gpr,rgpr, prefix='GPR')

    def eDDPR(self, gamma=None, update=False):
        if update:
            self.GPRa.gamma = gamma
        eddpr = self.GPRa.eDDPR(return_type="score", gamma=gamma, update=update)
        reddpr = self.GPRa.eDDPR_ranks()
        self.eddpr_dic = self.get_dict(eddpr,reddpr, prefix='eDDPR')

    def eGPR(self, alpha=None, gamma=None, update=False):
        if update:
            self.GPRa.alpha = alpha
            self.GPRa.gamma = gamma
        egpr = self.GPRa.eGPR(return_type="score", alpha=alpha, gamma=gamma, update=update)
        regpr = self.GPRa.eGPR_ranks()
        self.egpr_dic = self.get_dict(egpr,regpr, prefix='eGPR')

    def get_dicts(self, items=None):
        if items is None:
            items = ['pr','wpr','ddpr','gpr','eddpr','egpr']
        else:
            items = [ k.lower() for k in items ]
        dic_list = []
        if 'pr' in items:
            if self.pr_dic is None:
                self.PR()
            dic_list.append(self.pr_dic)
        if 'wpr' in items:
            if self.wpr_dic is None:
                self.WPR()
            dic_list.append(self.wpr_dic)
        if 'ddpr' in items:
            if self.ddpr_dic is None:
                self.DDPR()
            dic_list.append(self.ddpr_dic)
        if 'gpr' in items:
            if self.gpr_dic is None:
                self.GPR()
            dic_list.append(self.gpr_dic)
        if 'eddpr' in items:
            if self.eddpr_dic is None:
                self.eDDPR()
            dic_list.append(self.eddpr_dic)
        if 'egpr' in items:
            if self.egpr_dic is None:
                self.eGPR()
            dic_list.append(self.egpr_dic)
        return dic_list

    def get_results(self, items=None):
        dic_list = self.get_dicts(items=items)
        result_df = self.oo.get_nodedf(items=dic_list)
        return result_df

    def get_summary(self):
        sum_df = self.oo.get_summary_df()
        return sum_df

    def output_summary(self, filename=None):
        self.oo.summarycsv(filename=filename)

    def All_to_csv(self, filename=None):
        items = ['pr','wpr','ddpr','gpr','eddpr','egpr']
        self.to_csv(filename, items=items)

    def to_csv(self, filename=None, items=None):
        dic_list = self.get_dicts(items=items)
        self.oo.to_csv(filename=filename, items=dic_list)

    def All_to_shps(self, filename_prefix=None, crs=None):
        items = ['pr','wpr','ddpr','gpr','eddpr','egpr']
        self.to_shps(filename_prefix=filename_prefix, crs=crs, items=items)

    def to_shps(self, filename_prefix=None, crs=None, items=None):
        dic_list = self.get_dicts(items=items)
        self.oo.to_shps(filename_prefix=filename_prefix, crs=crs, items=dic_list)

    def to_nx(self, items=None):
        dic_list = self.get_dicts(items=items)
        ag,pos = self.oo.to_nx(items=dic_list)
        return (ag,pos)
