#!/bin/python
#coding:utf-8
from DouDiZhuPokerUtil import *

import roomai
import random
import copy

class DouDiZhuPokerEnv(roomai.AbstractEnv):

    def __init__(self):
        self.public_state  = PublicState()
        self.private_state = PrivateState() 

    def generate_initial_cards(self):
        cards = [];

        for i in xrange(13):
            for j in xrange(4):
                cards.append(i)
        cards.append(13)
        cards.append(14)
        random.shuffle(cards)

        handCards    = [[0 for j in xrange(15)] for i in xrange(3)]
        for i in xrange(len(cards)-3):
            idx = cards[i]
            handCards[i%3][idx] += 1

        keepCards = cards[-3:]

        self.private_state.hand_cards     =  handCards;
        self.private_state.additive_cards =  keepCards 
        self.num_hand_cards               =  [17,17,17] 
     
    def states2infos(self, infos):
        for i in xrange(4):
            infos[i].public_state = copy.deepcopy(self.public_state)
        infos[3].private_state    = copy.deepcopy(self.private_state)

    def update_license(self, turn, action):
        if action.pattern[0] != "i_cheat":
            self.public_state.license_playerid = turn
            self.public_state.license_action   = action 

    def update_cards(self, turn, action):
        if action.isComplemented() == False:
            action.complement()

        hand_cards = self.private_state.hand_cards[turn]
        for a in action.masterValues2Num:
            hand_cards[a] -= action.masterValues2Num[a]
        for a in action.slaveValues2Num:
            hand_cards[a] -= action.slaveValues2Num[a]
        
        self.num_hand_cards[turn] -= action.pattern[1] + action.pattern[4]


    def update_phase_bid2play(self):
        self.public_state.phase            = PhaseSpace.play
        
        self.public_state.landlord_id      = self.public_state.landlord_candidate_id
        self.public_state.license_playerid = self.public_state.turn        

        landlord_id    = self.public_state.landlord_id
        landlord_cards = self.private_state.hand_cards[landlord_id]
        additive_cards = self.private_state.additive_cards
        for c in additive_cards:
            landlord_cards[c] += 1
        self.private_state.num_hand_cards[landlord_id] += 3

    def is_action_from_cards(self,turn,action):

        flag = True
        if action.isComplemented() == False:
            action.complement()

        if action.pattern[0] == "i_cheat":      return True
        if action.pattern[0] == "i_bid":        return True
        if action.pattern[0] == "i_invalid":    return False
        
        hand_cards = self.private_state.hand_cards[turn]
       
        for a in action.masterValues2Num:
            flag = flag and (action.masterValues2Num[a] <= hand_cards[a])

        for a in action.slaveValues2Num:
            flag = flag and (action.slaveValues2Num[a] <= hand_cards[a])

        return flag    


    #@Override
    def isActionValid(self, action):
        if action.isComplemented() == False:
            action.complement()

        if action.pattern[0] == "i_invalid":
            return False;

        turn         = self.public_state.turn
        license_id   = self.public_state.license_playerid
        license_act  = self.public_state.license_action 
        phase        = self.public_state.phase

        if self.is_action_from_cards(turn, action) == False:
            return False

        if phase == PhaseSpace.bid:
            if action.pattern[0] not in ["i_cheat","i_bid"]:  
                return False
            return True
                
        if phase == PhaseSpace.play: 
            if action.pattern[0]  == "i_bid":  
                return False

            if license_id == turn:
                if action.pattern[0] == "i_cheat":  return False
                return True
            else:
                if action.pattern[0] == "i_cheat":  return True
                
                if action.pattern[6] > license_act.pattern[6]:  return True
                elif action.pattern[6] < license_act.pattern[6]:    return False
                elif action.maxMasterCard - license_act.maxMasterCard > 0:  return True
                else:   return False


    #@Overide
    def init(self, players):
         
        if len(players) != 3:
            raise Exception("The DouDiZhuPoker is a game with two players, len(players) = %d"%(len(players)))

        ## init the info
        infos  = [Info(), Info(), Info(), Info()]; 
        
        self.generate_initial_cards()
        
        self.public_state.firstPlayer       = int(random.random() * 3)
        self.public_state.turn              = self.public_state.firstPlayer
        self.public_state.phase             = PhaseSpace.bid
        self.public_state.epoch             = 0
        
        self.public_state.landlord_id       = -1
        self.public_state.license_playerid  = self.public_state.turn
        self.public_state.license_action    = None

        self.states2infos(infos)
        for i in xrange(3):
            infos[i].init_id         = i
            infos[i].init_cards      = self.private_state.hand_cards[i];

        return False, [], infos;


    ## we need ensure the action is valid
    #@Overide
    def forward(self, action):
        
        isTerminal   = False
        scores       = []
        infos        = [Info(), Info(), Info(), Info()]

        if action.isComplemented() == False:
            action.complement() 

        turn = self.public_state.turn
        turnNotChange = False

        if self.public_state.phase == PhaseSpace.bid:  
            
            if action.pattern[0] == "i_bid":
                self.public_state.landlord_candidate_id = turn

            new_landlord_candidate_id = self.public_state.landlord_candidate_id
            if self.public_state.epoch == 3 and new_landlord_candidate_id == -1:
                self.states2infos(infos)
                return True,[0,0,0], infos

            if (self.public_state.epoch == 2 and new_landlord_candidate_id != -1)\
                or self.public_state.epoch == 3:
                    self.update_phase_bid2play()
                    turnNotChange = True
                   
                    landlord_id = self.public_state.landlord_id
                    additive_cards = self.private_state.additive_cards
                    infos[landlord_id].init_addcards = copy.deepcopy(additive_cards)
        

        else: #phase == play

            if action.pattern[0] != "i_cheat":

                
                self.update_cards(turn,action)
                self.update_license(turn,action)                
    
                num = self.private_state.num_hand_cards[turn]
                if num == 0:
                    isTerminal = True
                    if turn == self.public_state.landlord_id:
                        scores = [-1,-1,-1]
                        scores[self.public_state.landlord_id] = 2
                    else:
                        scores = [1,1,1]
                        scores[self.public_state.landlord_id] = -2
                
 
        if turnNotChange == False:
            self.public_state.turn            = (turn+1)%3
        self.public_state.previous_id         = turn
        self.public_state.previous_action     = action
        self.public_state.epoch              += 1

        self.states2infos(infos) 

        return isTerminal, scores, infos


        

