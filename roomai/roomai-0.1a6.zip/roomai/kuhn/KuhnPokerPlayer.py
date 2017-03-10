#!/bin/python
#coding:utf-8
import random
import roomai.utils

class KuhnPokerAlwaysBetPlayer(roomai.utils.AbstractPlayer):
    def receiveInformation(self,p):
        pass
    def receiveValidActions(self,actions):
        self.actions = actions
    def receiveResult(self, result):
        pass
    def reset(self):
        pass
    def takeAction(self):
        return self.actions.bet;
   
   
a = """
class KuhnPokerCounterfactualRegretPlayer(AbstractPlayer):
    def reset(self):
        pass
    def __init__(self):
        self.InfoSet2ActionProb = dict();

    def receiveInformation(self,info):
        if "order" in info:
            self.order = info["order"]
        if "card" in info£º
            self.card  = info["card"]
        if "id" in info:
            self.id    = info["id"]

    def receiveValidActions(self,actions):
        self.actions = actions;

    def receiveResult(self, infoHistory, actionHistory, result):
        infoSet = "order:%d_card:%d"%(self.order, self.card) 

    def takeAction(self, infoHistory, actionHistory):
        initProb = dict();
        initProb[self.actions.bet]   = 0.5
        initProb[self.actions.cheat] = 0.5

        infoSet = "order:%d_card:%d"%(self.order, self.card)
        for a in actionHistory:
            infoSet += "_%d"%(a)
        
        if infoSet not in self.InfoSet2ActionProb:
            self.InfoSet2ActionProb[infoSet] = initProb

        actionPro = self.InfoSet2ActionProb[infoSet]
        r = random.random()
        sum1 = 0.0;
        for key in actionProb:
            sum1 += actionProb[key]
            if sum1 >= r:   return key
        return key
"""
