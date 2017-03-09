#!/bin/python
#coding=utf8

import sys
import roomai.doudizhu
import roomai.kuhn

#####################################################
                # environment list #
#####################################################
def createEnv(name):

    if name == "DouDiZhuEnv":
        return roomai.doudizhu.DouDiZhuPokerEnv()
    elif name == "KuhnEnv":
        return roomai.kuhn.KuhnPokerEnv()
    else: 
        raise KeyError("%s isn't a ChessEnvironment name"%(name))



#####################################################
                 # players list #
#####################################################
def createPlayer(name):

    if name == "DouDiZhuMaxPlayer":
        return roomai.doudizhu.DouDiZhuPokerMaxPlayer()
    elif name == "KuhnCounterfactualRegretPlayer":
        return roomai.kuhn.KuhnPokerCounterfactualRegretPlayer()
    elif name =="KuhnAlwaysBetPlayer":
        return roomai.kuhn.KuhnPokerAlwaysBetPlayer();

    else:
        raise KeyError("%s isn't a ChessPlayer name"%(name))

 
## is it easy to get you attentions
