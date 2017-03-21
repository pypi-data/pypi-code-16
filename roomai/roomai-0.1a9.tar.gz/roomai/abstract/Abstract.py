#!/bin/python
#coding=utf8

import copy

### abstract data struct
class AbstractPublicState:
    nothing = 0

class AbstractPrivateState:
    noting  = 0

class AbstractInfo:
    def __init__(self, public_state, private_state):
        self.public_state  = None
        self.private_state = None
    

### abstract 
class AbstractPlayer:
    def receiveInfo(self,info):
        raise NotImplementedError("The receiveInfo function hasn't been implemented") 
    def takeAction(self):
        raise NotImplementedError("The takeAction function hasn't been implemented") 
    def InvalidAction(self, action):
        raise NotImplementedError("The InvalidAction function hasn't been implemented")
    def ValidAction(self, action):
        raise NotImplementedError("The ValidAction function hasn't been implemented")
    def reset(self):
        raise NotImplementedError("The reset function hasn't been implemented")


class AbstractEnv:

    def __init__(self):
        self.public_state   = None
        self.private_state  = None

    def forward(self, actions):
        raise NotImplementedError("The receiveAction hasn't been implemented")

    def init(self):
        raise NotImplementedError("The init function hasn't been implemented")

    
'''
class Utils:
   

    @classmethod
    def is_action_valid(cls, public_state, action):
        raise NotImplementedError("The is_action_valid hasn't been implemented")

    @classmethod
    def squeeze_valid_action(cls, env, player):
        action = player.takeAction()
        count  = 0

        while self.is_action_valid(env.public_state, player) == False:
            player.InvalidAction(action)
            action  = player.takeAction()
            count  += 1

            if count > 1000:
                raise Exception("A player takes more than 1000 invalid actions in a epoch")

        player.ValidAction(action)

        return action

    @classmethod
    def round(cls, env, players):
    
        isTerminal, _, infos = env.init(players)

        for i in xrange(len(players)):
            players.receiveInformation(infos[i])
        
        count = 0
        while isTerminal == False: 
            turn = infos[-1].public_state.turn 
        
            action = self.squeeze_valid_action(env, players[turn])
            isTerminal, scores, infos = env.forward(action)
            for i in xrange(len(players)):
                players.receiveInformation(infos[i])

            count += 1
            if count > 10000:
                raise Exception("A round has more than 10000 epoches")

        return scores

'''
