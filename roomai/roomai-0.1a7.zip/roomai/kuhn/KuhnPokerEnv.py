#!/bin/python
import random
import math
import copy
import roomai.utils

class KuhnPokerEnv(roomai.utils.AbstractEnv):

    #@override
    def init(self,players):

        if len(players) != 2:
            raise Exception("KuhnPoker is a game with two players.")        

        self.private_state = PrivateState()
        card0 = math.floor(random.random() * 3)
        card1 = math.floor(random.random() * 3)
        while card0 == card1:
            card0 = math.floor(random.random() * 3)
        self.private_state.hand_cards = [card0, card1]

        self.public_state.turn          = int(math.floor(random.random() * 2))
        self.public_state.first         = self.private_state.turn
        self.public_state.epoch         = 0
        self.public_state.action_list   = []
        
        infos = self.gen_infos(2)
        infos[0].id = 0
        infos[0].card = card0
        infos[1].id = 1
        infos[1].card = card1
        
        return False, [], infos 

    #@override
    def forward(self, action):
        self.public_state.epoch += 1
        self.public_state.turn   = (self.public_state.turn+1)%2
        self.public_state.action_list.append(action)
        infos = self.gen_infos(2)

        if self.public_state.epoch == 1:
            return False, [], infos

        elif self.public_state.epoch == 2:
            scores = self.evaluteTwo()
            if scores[0] != -1:
                return true, scores, infos

        elif self.public_state.epoch == 3:
            scores = self.evaluteThree()
            return True, scores, infos

        else:
            raise Exception("KuhnPoker has 3 turns at most")

    
    def gen_infos(self,num):
        infos = [Info(), Info(), Info()]
        for i in xrange(num+1):
            infos[i].public_state = copy.deepcopy(self.public_state)
        infos[num].private_state = copy.deepcopy(self.private_state)

    def WhoHasHigherCard(self):
        hand_cards = self.private_state.hand_cards
        if hand_cards[0] > hand_cards[1]:
            return 0
        else:
            return 1

    def evaluteTwo(self, action):
        win    = self.WhoHasHigherCard()
        first  = self.public_state.first
        scores = [0, 0];
        actions = self.public_state.action_list
        
        if actions[0] == KuhnPokerActions.cheat and \
           actions[1] == KuhnPokerActions.bet:
            return [-1,-1]
        
        if actions[0] == actions[1] and \
           actions[0] == KuhnPokerActions.cheat:
            scores[win] = 1;
            return scores;

        if actions[0] == KuhnPokerActions.bet and \
           actions[1] == KuhnPokerActions.cheat:
            scores[first] = 1;
            return scores;

        if actions[0] == actions[1] and \
           actions[0] == KuhnPokerActions.bet:
            scores[win] = 2
            return scores;


    def evaluteThree(self):
        first   = self.public_state.first 
        win     = self.WhoHasHigherCard()
        scores  = [0, 0]
        if actions[2] == KuhnPokerActions.cheat:
            scores[1 - first] = 1;
        else:
            scores[win] = 2;
        return scores;
       
