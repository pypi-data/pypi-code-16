#!/bin/python
#coding:utf-8

import os
import roomai.utils
import copy
import itertools

#
#0, 1, 2, 3, ..., 7,  8, 9, 10, 11, 12, 13, 14
#^                ^   ^              ^       ^
#|                |   |              |       |
#3,               10, J, Q,  K,  A,  2,  r,  R
#

class PhaseSpace:
    bid  = 0
    play = 1

class ActionSpace:
    three   = 0;
    four    = 1;
    five    = 2;
    six     = 3;
    seven   = 4;
    eight   = 5;
    night   = 6;
    ten     = 7;
    J       = 8;
    Q       = 9;
    K       = 10;
    A       = 11;
    two     = 12;
    r       = 13;
    R       = 14;
    cheat   = 15;
    bid     = 16;

total_kind_cards = 15

class HandCards:
    def __init__(self, cards):
        self.cards      = [0 for i in xrange(total_kind_cards)]
        for c in cards:
            self.cards[c] += 1
        
        self.num_cards  = sum(self.cards)

        self.count2num  = [0 for i in xrange(total_kind_cards)]
        for num in self.cards:
            self.count2num[num] += 1

    def add_cards(self, cards):
        for c in cards:
            self.num_cards += 1
            self.count2num[self.cards[c]] -= 1
            self.cards[c] += 1
            self.count2num[self.cards[c]] += 1


    def remove_cards(self, cards):
        for c in cards:
            self.num_cards     -=1
            self.count2num[self.cards[c]] -= 1
            self.cards[c] -=1
            if self.cards[c] != 0:
                self.count2num[self.cards[c]] += 1

    def remove_action(self, action):
        self.remove_cards(action.masterCards)
        self.remove_cards(action.slaveCards)        

class Action:
    def __init__(self, masterCards, slaveCards):
        self.masterCards        = copy.deepcopy(masterCards)
        self.slaveCards         = copy.deepcopy(slaveCards)

        self.masterValues2Count = None
        self.slaveValues2Count  = None
        self.isMasterStraight   = None
        self.maxMasterCard      = None
        self.pattern            = None

        Utils.action2pattern(self)



class PrivateState(roomai.utils.AbstractPrivateState):
    def __init__(self):
        self.hand_cards     = [[],[],[]]
        self.keep_cards     = []

class PublicState(roomai.utils.AbstractPublicState):

    def __init__(self):

        self.landlord_candidate_id  = -1
        self.landlord_id            = -1
        self.license_playerid       = -1
        self.license_action         = None
        self.is_response            = False

        self.first_player           = -1
        self.turn                   = -1
        self.phase                  = -1
        self.epoch                  = -1

        self.previous_id            = -1
        self.previous_action        = None


class Info(roomai.utils.AbstractInfo):
    def __init__(self):
        ### init
        self.init_id            = -1
        self.init_cards         = []
        self.init_addcards      = []

        self.public_state       = None
        #In the info sent to players, the private info always be None.
        self.private_state      = None

class Utils(roomai.utils.AbstractUtils):

    @classmethod
    def is_action_valid(cls, hand_cards, public_state, action):

        if action.pattern[0] == "i_invalid":
            return False
    
        if Utils.is_action_from_handcards(hand_cards, action) == False:
            return False

        turn        = public_state.turn
        license_id  = public_state.license_playerid
        license_act = public_state.license_action
        phase       = public_state.phase

        if phase == PhaseSpace.bid:
            if action.pattern[0] not in ["i_cheat", "i_bid"]:
                return False
            return True

        if phase == PhaseSpace.play:
            if action.pattern[0] == "i_bid":    return False

            if license_id == turn:
                if action.pattern[0] == "i_cheat": return False
                return True

            else:
                if action.pattern[0] == "i_cheat":  return False

                if action.pattern[6] > license_act.pattern[6]:  return True
                elif action.pattern[6] < license_act.pattern[6]:    return False
                elif action.maxMasterCard - license_act.maxMasterCard > 0:  return True
                else:   return False


    @classmethod
    def is_action_from_handcards(cls, hand_cards, action):
            flag = True
            if action.pattern[0] == "i_cheat":  return True
            if action.pattern[0] == "i_bid":    return True
            if action.pattern[0] == "i_invalid":    return False

            for a in action.masterValues2Count:
                flag = flag and (action.masterValues2Count[a] <= hand_cards.cards[a])
            for a in action.slaveValues2Count:
                flag = flag and (action.slaveValues2Count[a] <= hand_cards.cards[a])
            return flag

    @classmethod
    def action2pattern(cls,action):

        action.masterValues2Count   = dict()
        for c in action.masterCards:
            if c in action.masterValues2Count:
                action.masterValues2Count[c] += 1
            else:
                action.masterValues2Count[c]  = 1

        action.slaveValues2Count    = dict()
        for c in action.slaveCards:
            if c in action.slaveValues2Count:
                action.slaveValues2Count[c] += 1
            else:
                action.slaveValues2Count[c]  = 1

        action.isMasterStraight = 0
        num = 0
        for v in action.masterValues2Count:
            if (v + 1) in action.masterValues2Count and (v+1) < ActionSpace.two: 
                num += 1
        if num == len(action.masterValues2Count) -1 and len(action.masterValues2Count) != 1:
            action.isMasterStraight = 1

        action.maxMasterCard = -1
        for c in action.masterValues2Count:
            if action.maxMasterCard < c:
                action.maxMasterCard = c

        
        ########################
        ## action 2 pattern ####
        ########################


        # is cheat?
        if len(action.masterCards) == 1 \
            and len(action.slaveCards) == 0 \
            and action.masterCards[0] == ActionSpace.cheat:
                action.pattern = AllPatterns["i_cheat"]

        # is roblord
        elif len(action.masterCards) == 1 \
            and len(action.slaveCards) == 0 \
            and action.masterCards[0] == ActionSpace.bid:
                action.pattern = AllPatterns["i_bid"] 

        # is twoKings
        elif len(action.masterCards) == 2 \
            and len(action.masterValues2Count) == 2\
            and len(action.slaveCards) == 0 \
            and action.masterCards[0] in [ActionSpace.r, ActionSpace.R] \
            and action.masterCards[1] in [ActionSpace.r, ActionSpace.R]:
                 action.pattern = AllPatterns["x_rocket"]
            
        else:

            ## process masterCards
            masterValues = action.masterValues2Count
            if len(masterValues) > 0:
                count = masterValues[action.masterCards[0]]
                for c in masterValues:
                    if masterValues[c] != count:    
                        action.pattern = AllPatterns["i_invalid"]


            ## process slave card
            action.slaveValues = action.slaveValues2Count
            if len(action.slaveValues) > 0:
                count = action.slaveValues[action.slaveCards[0]]
                for c in action.slaveValues:
                    if action.slaveValues[c] != count: 
                        action.pattern = AllPatterns["i_invalid"]

           
            if action.pattern == None:
                pattern = "p_%d_%d_%d_%d_%d"%(  len(action.masterCards), len(masterValues),\
                                                action.isMasterStraight,\
                                                len(action.slaveCards),  len(action.slaveValues))

                if pattern in AllPatterns:
                    action.pattern = AllPatterns[pattern]
                else:
                    action.pattern = AllPatterns["i_invalid"]



        return action

    @classmethod
    def extractStraight(cls, hand_cards, numStraightV, count, exclude):
            cardss = []

            if numStraightV == 0:
                return cardss
            c = 0
            for i in xrange(11,-1,-1): 
                if i in exclude:
                    c  = 0 
                elif hand_cards.cards[i] >= count:
                    c += 1
                else:
                    c  = 0        

                if c >= numStraightV:
                    cardss.append(range(i,i+numStraightV))

            return cardss          

    @classmethod        
    def extractDiscrete(cls, hand_cards, numDiscreteV, count, exclude):
            cardss  = []
            if numDiscreteV == 0:
                return cardss

            candidates = []
            for c in xrange(len(hand_cards.cards)):
                if (hand_cards.cards[c] >= count) and (c not in exclude):
                    candidates.append(c)
            if len(candidates) < numDiscreteV:  
                return cardss

            return list(itertools.combinations(candidates, numDiscreteV)) 


    
    @classmethod
    def candidate_actions(cls, hand_cards, public_state):

        patterns = []
        if public_state.phase == PhaseSpace.bid:
            patterns.append(AllPatterns["i_cheat"])
            patterns.append(AllPatterns["i_bid"])            
        else:       
            if public_state.is_response == False:
                for p in AllPatterns:
                    if p != "i_cheat" and p != "i_invalid":
                        patterns.append(AllPatterns[p])
            else:
                patterns.append(public_state.license_action.pattern)
                if public_state.license_action.pattern[6] == 1:
                    patterns.append(AllPatterns["p_4_1_0_0_0"])  #rank = 10
                    patterns.append(AllPatterns["x_rocket"])     #rank = 100            
                if public_state.license_action.pattern[6] == 10:
                    patterns.append(AllPatterns["x_rocket"])     #rank = 100
                patterns.append(AllPatterns["i_cheat"])


        actions = []             
        for pattern in patterns:    

            MasterNum   = pattern[1]
            MasterVNum  = pattern[2]
            isStraight  = pattern[3]
            SlaveNum    = pattern[4]
            SlaveVNum   = pattern[5]
            MasterCount  = -1
            SlaveCount   = -1

            if MasterNum > 0:
                MasterCount  = MasterNum/MasterVNum
            if SlaveVNum  > 0:
                SlaveCount   = SlaveNum /SlaveVNum



            if "i_invalid" == pattern[0]:
                 continue

            if "i_cheat" == pattern[0]:
                actions.append(Action([ActionSpace.cheat],[]))
                continue    

            if "i_bid" == pattern[0]:
                actions.append(Action([ActionSpace.bid],[]))
                continue

            if pattern[0] == "x_rocket":
                if  hand_cards.cards[ActionSpace.r] == 1 and \
                    hand_cards.cards[ActionSpace.R] == 1:
                    action = Action([ActionSpace.r, ActionSpace.R],[])
                    actions.append(action)
                continue       

            if pattern[1] + pattern[4] > hand_cards.num_cards:
                continue

            sum1 = 0
            for count in xrange(MasterCount,5,1):
                sum1 += hand_cards.count2num[count]
            if sum1 < MasterVNum:
                continue
            
            mCardss = []
            if isStraight == 1:
                mCardss = Utils.extractStraight(hand_cards, MasterVNum, MasterCount, [])
            else:
                mCardss = Utils.extractDiscrete(hand_cards, MasterVNum, MasterCount, [])


            for mCards in mCardss:
                m = []
                for mc in mCards:
                    m.extend([mc for i in xrange(MasterCount)])
                m.sort()
              
                if  SlaveVNum == 0:
                    actions.append(Action(copy.deepcopy(m), []))
                    continue

                sCardss = Utils.extractDiscrete(hand_cards, SlaveVNum, SlaveCount, mCards)
                for sCards in sCardss:
                    s = []
                    for sc in sCards:
                        s.extend([sc for i in xrange(SlaveCount)])
                    s.sort()
                    actions.append(Action(copy.deepcopy(m), s))

        return actions

path = os.path.split(os.path.realpath(__file__))[0]
AllPatterns  = dict();
file1 = open(path+"/patterns.txt")
for line in file1:
    line = line.replace(" ","").strip()
    line = line.split("#")[0]
    if len(line) == 0:  continue
    lines = line.split(",")

    for i in xrange(1,len(lines)):
        lines[i] = int(lines[i])
    AllPatterns[lines[0]] = lines
file1.close()

AllActions = dict();
action_file = open(path+"/actions.txt")
for line in action_file:
    line  = line.replace(" ","").strip()
    lines = line.split("\t")

    m   = []
    ms  = lines[0].split(",")
    for c in ms:
        if c != "":
            m.append(int(c))
    
    s   = []
    ss  = []
    if len(lines) == 2:
        ss  = lines[1].split(",")
    for c in ss:
        if c != "":
            s.append(int(c))

    if line in AllActions:
        print line
        print AllActions[line].masterCards, AllActions[line].slaveCards

    AllActions[line] = Action(m,s)

action_file.close()

print len(AllActions)

