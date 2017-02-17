# -*- coding: UTF-8 -*-

"""
caculation core
"""

#import os
import numpy
#import csv
import math
import pandas as pd
#import bigfloat
#import mpmath

class GPRs(object):
    def __init__(self):
        self.initialized = False

    def initialize(self, readfile, iteration=50000, alpha=1., beta=1., gamma=1.):
        ## alpha: should be integer(>=0), for the indegree
        ## beta: should be integer or float (>=0.), for distance (powerlaw decay), the higher beta lead to higher distance-decay effect
        ## gamma: should be float (0.<=gamma<=1.), for distance-decay (exponential), the less gamma lead to higher distance-decay effect
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        ## the above will be updated if updated happened, the below will remain same after update, and will be used if the three params are set to None
        self.init_alpha = alpha
        self.init_beta = beta
        self.init_gamma = gamma
        #self.t_threshold = t_threshold
        self.iteration = iteration
        self.node = readfile.nodes
        self.link = readfile.links
        self.matrix = readfile.matrix
        self.dmin = readfile.dmin
        self.dmax = readfile.dmax
        self.loc_nodes = readfile.loc_nodes

        self.nn = None
        self.matequal = None
        self.matindegree = None
        self.PR_initial = None
        self.preparation()

        self.degree = self.degree()

        self.pr = None
        self.wpr = None
        self.ddpr = None
        self.gpr = None
        self.eddpr = None
        self.egpr = None

        self.pr_rank = None
        self.wpr_rank = None
        self.ddpr_rank = None
        self.gpr_rank = None
        self.eddpr_rank = None
        self.egpr_rank = None

        self.initialized = True

    def getDgamma(self, gamma, dmin, dmax):
        # gamma is a proportion from 0.0 to 1.0
        # d0, dgamma is a distance in same unit
        d0 = gamma * (dmax - dmin) + dmin
        return d0

    def preparation(self):
        self.nn = len(self.node)
        col_sum = self.matrix.sum(axis=0)
        row_sum = self.matrix.sum(axis=1)

        count_node = sum(1 for x in col_sum if x > 0)

        # prepare initial score
        PR_initial = numpy.zeros((len(col_sum),1))
        for m in range(len(col_sum)):
            if col_sum[m] > 0:
                PR_initial[m][0] = (1.0 / count_node)

        # prepare transition matrix which is distributed proportional to indegree for Weighted PR
        matindegree = row_sum

        # prepare equally distributed transition matrix for original PR
        matequal = numpy.zeros((self.nn,1))
        for n in range(self.nn):
            if matindegree[n] > 0:
                matequal[n] = 1.0

        self.matequal = matequal
        self.matindegree = matindegree
        self.PR_initial = PR_initial

    # make transition matrix for DDPR and GPR
    def transmatG(self, attractiveness, decayfunction, alpha, beta, dgamma):
        mat_gravity_each = numpy.zeros((self.nn,self.nn))
        if decayfunction == "powerlaw":
            for m in range(self.nn):
                attrc_now = float(attractiveness[m])**alpha
                for n in range(self.nn):
                    if self.matrix[m][n] == 1:
                        distance = self.distancebetween(m+1,n+1) #/ 1000.0
                        mat_gravity_each[m][n] = attrc_now / (distance**beta)
        elif decayfunction == "exponential":
            for m in range(self.nn):
                attrc_now = float(attractiveness[m])**alpha
                for n in range(self.nn):
                    if self.matrix[m][n] == 1:
                        distancebeta = self.distancebetween(m+1,n+1)
                        mat_gravity_each[m][n] = attrc_now / math.exp(distancebeta / dgamma)
        else:
            for m in range(self.nn):
                attrc_now = float(attractiveness[m])**alpha
                for n in range(self.nn):
                    if self.matrix[m][n] == 1:
                        mat_gravity_each[m][n] = attrc_now

        mge_colsum = mat_gravity_each.sum(axis=0)
        mat_gravity = numpy.matrix(numpy.zeros((self.nn,self.nn)))
        for m in range(self.nn):
            for n in range(self.nn):
                if mge_colsum[n] != 0:
                    mat_gravity.itemset((m,n), (mat_gravity_each[m][n] / mge_colsum[n]))
        return mat_gravity

    # calculation of distance between two nodes (simply Pythagoras' theorem)
    def distancebetween(self,node1,node2):
        x1, y1 = self.node[node1]
        x2, y2 = self.node[node2]
        dist = float(math.sqrt((x1-x2)**2 + (y1-y2)**2))
        return dist

    def degree(self):
        return self.matindegree

    # finally, calculating the four PRs
    def generic_PRa(self, transitionmatrix):
        return numpy.dot((transitionmatrix**self.iteration), self.PR_initial)

    def ranking(self, score):
        df0 = score.A
        df  = pd.DataFrame(df0)
        ranks = df.rank(method='average')
        return numpy.array(ranks)

    def PR(self, return_type="score"):
        if self.pr is None:
            self.pr = self.generic_PRa(self.transmatG(self.matequal, "notdecay", 0., None, None))
        if return_type=="score":
            return self.pr
        elif return_type=="rank":
            if self.pr_rank is None:
                self.pr_rank = self.ranking(self.pr)
            return self.pr_rank
        else:
            raise NameError("return_type must be either score or rank")

    def WPR(self, alpha=None, update=False, return_type="score"):
        if (update or (self.wpr is None)):
            if alpha is None:
                alpha = self.init_alpha
            self.wpr = self.generic_PRa(self.transmatG(self.matindegree, "notdecay", alpha, None, None))
        if return_type=="score":
            return self.wpr
        elif return_type=="rank":
            if self.wpr_rank is None:
                self.wpr_rank = self.ranking(self.wpr)
            return self.wpr_rank
        else:
            raise NameError("return_type must be either score or rank")

    def DDPR(self, beta=None, update=False, return_type="score"):
        if (update or (self.ddpr is None)):
            if beta is None:
                beta = self.init_beta
            self.ddpr = self.generic_PRa(self.transmatG(self.matequal, "powerlaw", 0., beta, None))
        if return_type=="score":
            return self.ddpr
        elif return_type=="rank":
            if self.ddpr_rank is None:
                self.ddpr_rank = self.ranking(self.ddpr)
            return self.ddpr_rank
        else:
            raise NameError("return_type must be either score or rank")

    def GPR(self, alpha=None, beta=None, update=False, return_type="score"):
        if (update or (self.gpr is None)):
            if alpha is None:
                alpha = self.init_alpha
            if beta is None:
                beta = self.init_beta
            self.gpr = self.generic_PRa(self.transmatG(self.matindegree, "powerlaw", alpha, beta, None))
        if return_type=="score":
            return self.gpr
        elif return_type=="rank":
            if self.gpr_rank is None:
                self.gpr_rank = self.ranking(self.gpr)
            return self.gpr_rank
        else:
            raise NameError("return_type must be either score or rank")

    def eDDPR(self, gamma=None, update=False, return_type="score"):
        if (update or (self.eddpr is None)):
            if gamma is None:
                gamma = self.init_gamma
            dgamma = self.getDgamma(gamma, self.dmin, self.dmax)
            self.eddpr = self.generic_PRa(self.transmatG(self.matequal, "exponential", 0., None, dgamma))
        if return_type=="score":
            return self.eddpr
        elif return_type=="rank":
            if self.eddpr_rank is None:
                self.eddpr_rank = self.ranking(self.eddpr)
            return self.eddpr_rank
        else:
            raise NameError("return_type must be either score or rank")

    def eGPR(self, alpha=None, gamma=None, update=False, return_type="score"):
        if (update or (self.egpr is None)):
            if alpha is None:
                alpha = self.init_alpha
            if gamma is None:
                gamma = self.init_gamma
            dgamma = self.getDgamma(gamma, self.dmin, self.dmax)
            self.egpr = self.generic_PRa(self.transmatG(self.matindegree, "exponential", alpha, None, dgamma))
        if return_type=="score":
            return self.egpr
        elif return_type=="rank":
            if self.egpr_rank is None:
                self.egpr_rank = self.ranking(self.egpr)
            return self.egpr_rank
        else:
            raise NameError("return_type must be either score or rank")



    def PR_ranks(self):
        if self.pr is None:
            pr = self.PR()
        return self.ranking(self.pr)

    def WPR_ranks(self, alpha=None, update=False):
        if (update or (self.wpr is None)):
            wpr = self.WPR(alpha=alpha, update=update)
        return self.ranking(self.wpr)

    def DDPR_ranks(self, beta=None, update=False):
        if (update or (self.ddpr is None)):
            ddpr = self.DDPR(beta=beta, update=update)
        return self.ranking(self.ddpr)

    def GPR_ranks(self, alpha=None, beta=None, update=False):
        if (update or (self.gpr is None)):
            gpr = self.GPR(alpha=alpha, beta=beta, update=update)
        return self.ranking(self.gpr)

    def eDDPR_ranks(self, gamma=None, update=False):
        if (update or (self.eddpr is None)):
            eddpr = self.eDDPR(gamma=gamma, update=update)
        return self.ranking(self.eddpr)

    def eGPR_ranks(self, alpha=None, gamma=None, update=False):
        if (update or (self.egpr is None)):
            egpr = self.eGPR(alpha=alpha, gamma=gamma, update=update)
        return self.ranking(self.egpr)
