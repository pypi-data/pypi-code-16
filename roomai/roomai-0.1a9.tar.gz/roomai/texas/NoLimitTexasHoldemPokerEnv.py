#!/bin/python
#coding:utf-8

import random
import copy
import roomai.abstract

from NoLimitTexasHoldemPokerUtil import *

class NoLimitTexasHoldemPokerEnv(roomai.abstract.AbstractEnv):

    def __init__(self):
        self.num_players    = 3 
        self.big_blind_id   = int(random.random() * 3)
        self.small_blind_id = (self.big_blind_id + 1 ) % 3  
 
    def state2info(self):
        infos = [Info(), Info(), Info()]
        for i in xrange(len(infos)):
            infos[i].public_state = copy.deepcopy(self.public_state)
        infos[len(infos)-1].private_state = copy.deepcopy(self.private_state)        

    def compute_scores(self, win_id):
        num_players = len(self.private_state.hand_cards)
        scores      = [0 for i in xrange(num_players)]
        sum1        = sum(self.chips)
        scores[win_id] = sum1
        for i in xrange(len(self.private_state.hand_cards)):
            if i == win_id: continue
            scores[i] =  -self.public_state.chips[i]
        return scores
    
    def a_round_end(self):
        
     

    #@override
    def init(self):
        isTerminal = False
        scores     = []
        
        self.public_state               = PublicState()
        self.public_state.chips         = [0 for i in xrange(self.num_players)]
        self.public_state.big_blind_id  = self.big_blind_id
        self.public_state.small_blind_id= self.small_blind_id
        self.public_state.chips[self.public_state.big_blind_id]     = 10
        self.public_state.chips[self.public_state.small_blind_id]   = 5        
        self.public_state.turn              = self.public_state.small_blind_id
        self.public_state.license_id        = self.public_state.big_blind_id
        self.public_state.is_quit           = [False for i in xrange(self.num_players)] 
        self.public_state.public_cards      = []
        self.public_state.previous_id       = -1
        self.public_state.previous_action   = None

        self.private_state = PrivateState() 
        allcards = []
        for i in xrange(13):
            for j in xrange(4):
                allcards.append(Card(i,j))
        random.shuffle(allcards)        
        self.private_state.hand_cards       = [[] for i in xrange(self.num_players)]
        for i in xrange(self.num_players):
            self.private_state.hand_cards[i]    = allcards[i*2:(i+1)*2]
        self.private_state.keep_cards   = allcards[self.num_players*2:self.num_players*2+5]         
        
        #gen info
        infos = self.state2infos()
        for i in xrange(2):
            infos[i].player_id = i
        
        return isTerminal, scores, infos

    ## we need ensure the action is valid
    #@Overide
    def forward(self, action):
        isTerminal = False
        ps         = self.public_state
        turn = self.public_state.turn

        if action.option == ActionSpace.quit:
            self.is_quit[turn] = True
            if (turn + 1)%ps.num_players == ps.license_id:
                    

        elif action.option == ActionSpace.check:
            pass
        
        elif action.option == ActionSpace.bet:
            pass            
                      
        
        turn += 1
        while ps.is_quit[turn] == True:
            turn += 1
        if turn == ps.license_id:
             
        
