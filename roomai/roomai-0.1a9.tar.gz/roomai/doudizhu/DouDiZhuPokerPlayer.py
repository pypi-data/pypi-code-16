#!/bin/python
import roomai
import random
from DouDiZhuPokerUtils import *

class DouDiZhuPokerRandomPlayer(roomai.abstract.AbstractPlayer):
    
    def __init__(self):
        self.id1            = None
        self.hand_cards     = None
        self.public_state   = None
    
    #@override    
    def receiveInfo(self,info):
        if info.init_id != -1:
            self.id1 = info.init_id
        if info.init_cards != []:
            self.hand_cards = info.init_cards
        if info.init_addcards != [] and info.public_state.landlord_id == self.id1:
            self.hand_cards.add_cards(info.init_addcards)
        
        self.public_state = info.public_state

    #@override
    def takeAction(self):
        candidates = Utils.candidate_actions(self.hand_cards, self.public_state).values()
        idx = int(random.random() * len(candidates))
        action = candidates[idx]
        self.hand_cards.remove_action(action)
        return action

    #@override
    def InvalidAction(self, action):
        pass

    #@override
    def ValidAction(self, action):
        pass
    
    #@override
    def reset(self, action):
        self.id1            = None
        self.hand_cards     = None
        self.public_state   = None
