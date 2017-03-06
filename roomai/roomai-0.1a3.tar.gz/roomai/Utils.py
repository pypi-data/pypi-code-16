#!/bin/python
#coding=utf8

from AbstractEnvPlayer import *

def squeezeValidAction(env, player):
    action = player.takeAction()
    count  = 0

    while evn.isActionValid(action) == False:
        player.InvalidAction(action)
        action  = player.takeAction()
        count  += 1

        if count < 1000:
            raise Exception("A player takes more than 1000 invalid actions in a epoch")

  
    player.ValidAction(action)
    return action

def round(env, players):
    
    isTerminal, _, infos = env.init(players)
    while isTerminal == False: 
        turn = infos[-1].public_state.turn 
        
        action = squeezeValidAction(env, players[turn])
        isTerminal, scores, infos = env.forward(action)

    return scores
