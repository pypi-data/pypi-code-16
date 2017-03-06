#!/bin/python
#coding=utf8

class AbstractPlayer:
    def receiveValidActions(self, actions):
        raise NotImplementedError("The receiveValidActions function hasn't been implemented")
    def receiveInformation(self,info):
        raise NotImplementedError("The receiveInformation function hasn't been implemented")
    
    def takeAction(self):
        raise NotImplementedError("The takeAction function hasn't been implemented") 

    def InvalidAction(self, action):
        raise NotImplementedError("The InvalidAction function hasn't been implemented")

    def ValidAction(self, action):
        raise NotImplementedError("The ValidAction function hasn't been implemented")


    def reset(self):
        raise NotImplementedError("The reset function hasn't been implemented")


class AbstractEnv:

    #@Return isTerminal, scores,  nextTurnInformations,     nextTurnValidActions
    #The return variables are used for the next turn
    def forward(self, actions):
        raise NotImplementedError("The receiveAction hasn't been implemented")

    #@Return isTerminal, scores,  fistTurnInformation,      firstTurnValidActions
    def init(self, players):
        raise NotImplementedError("The init function hasn't been implemented")

   ### 
    def isValidAction(self, action):
        raise NotImplementedError("The isValidAction function hasn't been implemented")

    #squeeze valid action from player.
    #This function is necessary since the player may take a invalid action


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
