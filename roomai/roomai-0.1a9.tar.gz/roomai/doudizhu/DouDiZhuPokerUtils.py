#!/bin/python
#coding:utf-8

import os
import roomai.abstract
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

class ScopeSpace:
    iresponse_stage = 0
    response_stage  = 1
    all_stage       = 2

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
            if c < 0 or c >= 15: continue
            self.num_cards += 1
            self.count2num[self.cards[c]] -= 1
            self.cards[c] += 1
            self.count2num[self.cards[c]] += 1


    def remove_cards(self, cards):
        for c in cards:
            if c < 0 or c >= 15: continue
            self.num_cards     -=1
            self.count2num[self.cards[c]] -= 1
            self.cards[c] -=1
            self.count2num[self.cards[c]] += 1

    def remove_action(self, action):
        self.remove_cards(action.masterCards)
        self.remove_cards(action.slaveCards)        

class Action:
    def __init__(self, masterCards, slaveCards):
        self.masterCards        = copy.deepcopy(masterCards)
        self.slaveCards         = copy.deepcopy(slaveCards)

        self.masterPoints2Count = None
        self.slavePoints2Count  = None
        self.isMasterStraight   = None
        self.maxMasterPoint     = None
        self.minMasterPoint     = None
        self.pattern            = None
        Utils.action2pattern(self)

                
        if self.pattern[0] in ["i_invalid","i_bid"]:
            self.scope = ScopeSpace.all_stage
        
        elif self.pattern[0] == "i_cheat":
            self.scope = ScopeSpace.response_stage

        elif self.pattern[0] == "x_rocket":
            self.scope  = ScopeSpace.all_stage

        else:
            self.scope              = ScopeSpace.all_stage
            ##boom
            if self.pattern[0] == "p_3_1_0_1_0" and \
                self.masterCards[0] == self.slaveCards[0]:
                self.scope = ScopeSpace.response_stage
            
            ##3 plane
            if  self.pattern[0] == "p_9_3_1_3_0" and \
                self.slavePoints2Count[self.slaveCards[0]]  == 3 and \
                (self.minMasterPoint -1 == self.slaveCards[0] or \
                 self.maxMasterPoint +1 == self.slaveCards[0]):
                self.scope = ScopeSpace.response_stage
                
            

class PrivateState(roomai.abstract.AbstractPrivateState):
    def __init__(self):
        self.hand_cards     = [[],[],[]]
        self.keep_cards     = []

class PublicState(roomai.abstract.AbstractPublicState):

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


class Info(roomai.abstract.AbstractInfo):
    def __init__(self):
        ### init
        self.init_id            = -1
        self.init_cards         = []
        self.init_addcards      = []

        self.public_state       = None
        #In the info sent to players, the private info always be None.
        self.private_state      = None

class Utils:

    gen_allactions = False
    @classmethod
    def is_action_valid(cls, hand_cards, public_state, action):
        if cls.gen_allactions == True:
            return True

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

            if public_state.is_response == False:
                if action.scope == ScopeSpace.response_stage: return False
                return True

            else: #response
                if action.scope == ScopeSpace.iresponse_stage:  return False

                if action.pattern[0] == "i_cheat":  return True

                ## not_cheat
                if action.pattern[6] > license_act.pattern[6]:  return True
                elif action.pattern[6] < license_act.pattern[6]:    return False
                elif action.maxMasterPoint - license_act.maxMasterPoint > 0:  return True
                else:   return False


    @classmethod
    def is_action_from_handcards(cls, hand_cards, action):
            flag = True
            if action.pattern[0] == "i_cheat":  return True
            if action.pattern[0] == "i_bid":    return True
            if action.pattern[0] == "i_invalid":    return False

            for a in action.masterPoints2Count:
                flag = flag and (action.masterPoints2Count[a] <= hand_cards.cards[a])
            for a in action.slavePoints2Count:
                flag = flag and (action.slavePoints2Count[a] <= hand_cards.cards[a])
            return flag


    @classmethod
    def action2pattern(cls,action):

        action.masterPoints2Count   = dict()
        for c in action.masterCards:
            if c in action.masterPoints2Count:
                action.masterPoints2Count[c] += 1
            else:
                action.masterPoints2Count[c]  = 1

        action.slavePoints2Count    = dict()
        for c in action.slaveCards:
            if c in action.slavePoints2Count:
                action.slavePoints2Count[c] += 1
            else:
                action.slavePoints2Count[c]  = 1

        action.isMasterStraight = 0
        num = 0
        for v in action.masterPoints2Count:
            if (v + 1) in action.masterPoints2Count and (v+1) < ActionSpace.two: 
                num += 1
        if num == len(action.masterPoints2Count) -1 and len(action.masterPoints2Count) != 1:
            action.isMasterStraight = 1

        action.maxMasterPoint = -1
        action.minMasterPoint = 100
        for c in action.masterPoints2Count:
            if action.maxMasterPoint < c:
                action.maxMasterPoint = c
            if action.minMasterPoint > c:
                action.minMasterPoint = c

        
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
            and len(action.masterPoints2Count) == 2\
            and len(action.slaveCards) == 0 \
            and action.masterCards[0] in [ActionSpace.r, ActionSpace.R] \
            and action.masterCards[1] in [ActionSpace.r, ActionSpace.R]:
                 action.pattern = AllPatterns["x_rocket"]
            
        else:

            ## process masterCards
            masterPoints = action.masterPoints2Count
            if len(masterPoints) > 0:
                count = masterPoints[action.masterCards[0]]
                for c in masterPoints:
                    if masterPoints[c] != count:    
                        action.pattern = AllPatterns["i_invalid"]



           
            if action.pattern == None:
                pattern = "p_%d_%d_%d_%d_%d"%(  len(action.masterCards), len(masterPoints),\
                                                action.isMasterStraight,\
                                                len(action.slaveCards),  0)

                if pattern in AllPatterns:
                    action.pattern = AllPatterns[pattern]
                else:
                    action.pattern = AllPatterns["i_invalid"]



        return action

    @classmethod
    def extractMasterCards(cls, hand_cards, numPoint, count, pattern):
        is_straight = pattern[3]
        cardss = []
        ss = []

        if numPoint == 0:
                return cardss

        if is_straight == 1:
            c = 0
            for i in xrange(11,-1,-1): 
                if hand_cards.cards[i] >= count:
                    c += 1
                else:
                    c  = 0        

                if c >= numPoint:
                    ss.append(range(i,i+numPoint))
        else:
            candidates = []
            for c in xrange(len(hand_cards.cards)):
                if hand_cards.cards[c] >= count:
                    candidates.append(c)
            if len(candidates) < numPoint:
                    return []
            ss =  list(itertools.combinations(candidates, numPoint))
       
        for set1 in ss:
            s = []
            for c in set1:
                for i in xrange(count):
                    s.append(c)
            s.sort()
            cardss.append(s) 

        return cardss

    @classmethod        
    def extractSlaveCards(cls, hand_cards, numCards, used_cards, pattern):
            used = [0 for i in xrange(15)]
            for p in used_cards:
                used[p] += 1

            numMaster       = pattern[1]
            numMasterPoint  = pattern[2]
            numSlave        = pattern[4]

            candidates = []
            res1       = []
            res        = []
                        
            if numMaster / numMasterPoint == 3:

                if numSlave / numMasterPoint == 1: # single
                    for c in xrange(len(hand_cards.cards)):
                        for i in xrange(hand_cards.cards[c] - used[c]):
                            candidates.append(c)
                    if len(candidates) >= numCards:
                        res1 = list(set(list(itertools.combinations(candidates, numCards))))
                    for sCard in res1:  res.append([x for x in sCard])                

                elif numSlave / numMasterPoint == 2: #pair
                    for c in xrange(len(hand_cards.cards)):
                        for i in xrange((hand_cards.cards[c] - used[c])/2):
                            candidates.append(c)
                    if len(candidates) >= numCards / 2:
                        res1 = list(set(list(itertools.combinations(candidates, numCards/2))))
                    for sCard in res1:
                        tmp = [x for x in sCard]
                        tmp.extend([x for x in sCard])   
                        res.append(tmp)                 

            elif numMaster/ numMasterPoint == 4:

                if numSlave / numMasterPoint == 2: #single
                    for c in xrange(len(hand_cards.cards)):
                        for i in xrange(hand_cards.cards[c] - used[c]):
                            candidates.append(c)
                    if len(candidates) >= numCards:
                        res1 = list(set(list(itertools.combinations(candidates, numCards))))
                    for sCard in res1:  res.append([x for x in sCard])                
                        

                elif numSlave / numMasterPoint == 4: # pair
                    for c in xrange(len(hand_cards.cards)):
                        for i in xrange((hand_cards.cards[c] - used[c])/2):
                            candidates.append(c)
                    if len(candidates) >= numCards / 2:
                        res1 = list(set(list(itertools.combinations(candidates, numCards/2))))
                    for sCard in res1:
                        tmp = [x for x in sCard]
                        tmp.extend([x for x in sCard])   
                        res.append(tmp)                 

            return res
        

    @classmethod
    def lookup_action(cls, masterCards, slaveCards):
        masterCards.sort()
        slaveCards.sort()

        mStr = ""
        for c in masterCards:
            mStr += "%d,"%(c)
        sStr = ""
        for c in slaveCards:
            sStr += "%d,"%(c)

        line = "%s\t%s\n"%(mStr,sStr)
        line = line.replace(" ","")
        line = line.strip()
        
        if cls.gen_allactions == True:
            return line, Action(masterCards, slaveCards)

        if line in AllActions:
            return line,AllActions[line]
        else:             
            raise Exception(line + "is not in AllActions") 

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

        is_response = public_state.is_response
        license_act = public_state.license_action
        actions     = dict()           

        for pattern in patterns:    
            numMaster       = pattern[1]
            numMasterPoint  = pattern[2]
            isStraight      = pattern[3]
            numSlave        = pattern[4]
            MasterCount     = -1
            SlaveCount      = -1

            if numMaster > 0:
                MasterCount  = numMaster/numMasterPoint

            if "i_invalid" == pattern[0]:
                 continue
            
            if "i_cheat" == pattern[0]:
                key,action = cls.lookup_action([ActionSpace.cheat],[])
                if cls.is_action_valid(hand_cards, public_state, action) == True:
                    actions[key] = action
                continue    

            if "i_bid" == pattern[0]:
                key,action = cls.lookup_action([ActionSpace.bid],[])
                if cls.is_action_valid(hand_cards, public_state, action) == True:
                    actions[key] = action
                continue

            if pattern[0] == "x_rocket":
                if  hand_cards.cards[ActionSpace.r] == 1 and \
                    hand_cards.cards[ActionSpace.R] == 1:
                    key,action = cls.lookup_action([ActionSpace.r, ActionSpace.R],[])
                    if cls.is_action_valid(hand_cards, public_state, action) == True:
                        actions[key] = action
                continue       
            

            if pattern[1] + pattern[4] > hand_cards.num_cards:
                continue
            sum1 = 0
            for count in xrange(MasterCount,5,1):
                sum1 += hand_cards.count2num[count]
            if sum1 < numMasterPoint:
                continue
           
            ### action with cards
            mCardss = []
            mCardss = Utils.extractMasterCards(hand_cards, numMasterPoint, MasterCount, pattern)
            

            for mCards in mCardss:
                if  numSlave == 0:
                    key,action = cls.lookup_action(mCards,[])
                    if cls.is_action_valid(hand_cards, public_state, action) == True:
                        actions[key] = action
                    continue
               
                sCardss = Utils.extractSlaveCards(hand_cards, numSlave, mCards, pattern)
                for sCards in sCardss:
                    key, action = cls.lookup_action(mCards, sCards)
                    if cls.is_action_valid(hand_cards, public_state, action) == True:
                        actions[key] = action
        return actions


############## read data ################

import zipfile

def get_file(path):
    if ".zip" in path:
        lines = path.split(".zip")
        zip1  = zipfile.ZipFile(lines[0] + ".zip")
        len1  = len(lines[1])
        path  = lines[1][1:len1]
        return zip1.open(path)
    else:
        return open(path)

path = os.path.split(os.path.realpath(__file__))[0]
AllPatterns  = dict();
file1 = get_file(path+"/patterns.py")
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
action_file = get_file(path+"/actions.py")
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

    action              = Action(m,s)
    AllActions[line]    = action
action_file.close()


