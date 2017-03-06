#!/bin/python
#coding=utf8

import sys
import roomai.doudizhu
import roomai.kuhn


#####################################################
                # environment list #
#####################################################
def createEnv(name):

    if name == "doudizhuEnv":
        return roomai.doudizhu.doudizhuEnv()
    elif name == "kuhnEnv":
        return roomai.kuhn.kuhnEnv()
    else: 
        raise KeyError("%s isn't a ChessEnvironment name"%(name))



#####################################################
                 # players list #
#####################################################
def createPlayer(name):

    if name == "doudizhuMaxPlayer":
        return roomai.doudizhu.doudizhuMaxPlayer()
    elif name == "kuhnCounterfactualRegretPlayer":
        return roomai.kuhn.kuhnCounterfactualRegretPlayer()
    elif name =="kuhnAlwaysBetPlayer":
        return roomai.kuhn.kuhnAlwaysBetPlayer();

    else:
        raise KeyError("%s isn't a ChessPlayer name"%(name))

 
## is it easy to get you attentions
