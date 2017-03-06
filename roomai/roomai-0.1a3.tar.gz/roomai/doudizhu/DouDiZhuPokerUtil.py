#!/bin/python
#coding:utf-8


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

class PrivateState:
    def __init__(self):
        self.hand_cards         = [[],[],[]]
        self.num_hand_cards     = [-1,-1,-1]
        self.additive_cards     = []

class PublicState:

    def __init__(self):

        self.landlord_candidate_id  = -1
        self.landlord_id            = -1
        self.license_playerid         = -1
        self.license_action         = None

        self.first_player           = -1
        self.turn                   = -1
        self.phase                  = -1
        self.epoch                  = -1

        self.previous_id            = -1
        self.previous_action        = None


class Info:
    def __init__(self):
        ### init
        self.init_id            = -1
        self.init_cards         = []
        self.init_addcards      = []

        self.public_state       = None
        #In the info sent to players, the private info always be None.
        self.private_state      = None
        
        
class Action:
    def __init__(self, masterCards, slaveCards):
        self.masterCards        = masterCards
        self.slaveCards         = slaveCards

        self.masterValues2Num   = None
        self.slaveValues2Num    = None
        self.isMasterContinuous = None
        self.maxMasterCard      = None
        self.pattern            = None

    def isComplemented(self):

        flag = (self.masterValues2Num != None and \
                self.slaveValues2Num != None and \
                self.isMasterContinuous != None and \
                self.maxMasterCard  != None and \
                self.pattern != None)
        return flag

    def complement(self):

        self.masterValues2Num   = dict()
        for c in self.masterCards:
            if c in self.masterValues2Num:
                self.masterValues2Num[c] += 1
            else:
                self.masterValues2Num[c]  = 1

        self.slaveValues2Num    = dict()
        for c in self.slaveCards:
            if c in self.slaveValues2Num:
                self.slaveValues2Num[c] += 1
            else:
                self.slaveValues2Num[c]  = 1

        self.isMasterContinuous = 0
        num = 0
        for v in self.masterValues2Num:
            if (v + 1) in self.masterValues2Num and v < ActionSpace.two: 
                num += 1
        if num == len(self.masterValues2Num) -1 and len(self.masterValues2Num) != 1:
            self.isMasterContinuous = 1

        self.maxMasterCard = -1
        for c in self.masterValues2Num:
            if self.maxMasterCard < c:
                self.maxMasterCard = c

        
        ########################
        ## action 2 pattern ####
        ########################


        # is cheat?
        if len(self.masterCards) == 1 \
            and len(self.slaveCards) == 0 \
            and self.masterCards[0] == ActionSpace.cheat:
                self.pattern = AllPatterns["i_cheat"]

        # is roblord
        elif len(self.masterCards) == 1 \
            and len(self.slaveCards) == 0 \
            and self.masterCards[0] == ActionSpace.bid:
                self.pattern = AllPatterns["i_bid"] 

        # is twoKings
        elif len(self.masterCards) == 2 \
            and len(self.masterValues2Num) == 2\
            and len(self.slaveCards) == 0 \
            and self.masterCards[0] in [ActionSpace.r, ActionSpace.R] \
            and self.masterCards[1] in [ActionSpace.r, ActionSpace.R]:
                 self.pattern = AllPatterns["x_rocket"]
            
        else:

            ## process masterCards
            masterValues = self.masterValues2Num
            if len(masterValues) > 0:
                count = masterValues[self.masterCards[0]]
                for c in masterValues:
                    if masterValues[c] != count:    
                        self.pattern = AllPatterns["i_invalid"]


            ## process slave card
            slaveValues = self.slaveValues2Num
            if len(slaveValues) > 0:
                count = slaveValues[self.slaveCards[0]]
                for c in slaveValues:
                    if slaveValues[c] != count: 
                        self.pattern = AllPatterns["i_invalid"]

           
            if self.pattern == None:
                pattern = "p_%d_%d_%d_%d_%d"%(  len(self.masterCards), len(masterValues),\
                                                self.isMasterContinuous,\
                                                len(self.slaveCards),  len(slaveValues))

                if pattern in AllPatterns:
                    self.pattern = AllPatterns[pattern]
                else:
                    self.pattern = AllPatterns["i_invalid"]



        return self



AllPatterns  = dict();
#p_NumMasterCard_NumMasterValues_isContinous_NumSlaveCard_NumSlaveValues
#(name, NumMasterCard, NumMasterValues, isStraight(0,1), NumSlaveCard, NumSlaveValues,rank)
AllPatterns["i_invalid"]      =  ("i_invalid",       0,0,0,0,0,-1) #special process logic
AllPatterns["i_cheat"]        =  ("i_cheat",         1,1,0,0,0,-1) #special process logic
AllPatterns["i_bid"]          =  ("i_bid",           1,1,0,0,0,-1) #special process logic
AllPatterns["x_rocket"]       =  ("x_rocket",        2,2,1,0,0,100) #special process logic
AllPatterns["p_1_1_0_0_0"]    =  ("p_1_1_0_0_0",     1,1,0,0,0,1)
AllPatterns["p_2_1_0_0_0"]    =  ("p_2_1_0_0_0",     2,1,0,0,0,1) 
AllPatterns["p_3_1_0_0_0"]    =  ("p_3_1_0_0_0",     3,1,0,0,0,1) 
AllPatterns["p_4_1_0_0_0"]    =  ("p_4_1_0_0_0",     4,1,0,0,0,10) 
AllPatterns["p_3_1_0_1_1"]    =  ("p_3_1_0_1_1",     3,1,0,1,1,1)
AllPatterns["p_5_5_1_0_0"]    =  ("p_5_5_1_0_0",     5,5,1,0,0,1)
AllPatterns["p_3_1_0_2_1"]    =  ("p_3_1_0_2_1",     3,1,0,2,1,1)
AllPatterns["p_6_6_1_0_0"]    =  ("p_6_6_1_0_0",     6,6,1,0,0,1)
AllPatterns["p_6_3_1_0_0"]    =  ("p_6_3_1_0_0",     6,3,1,0,0,1)
AllPatterns["p_6_2_1_0_0"]    =  ("p_6_2_1_0_0",     6,2,1,0,0,1)
AllPatterns["p_4_1_0_2_2"]    =  ("p_4_1_0_2_2",     4,1,0,2,2,1)
AllPatterns["p_7_7_1_0_0"]    =  ("p_7_7_1_0_0",     7,7,1,0,0,1)
AllPatterns["p_8_8_1_0_0"]    =  ("p_8_8_1_0_0",     8,8,1,0,0,1)
AllPatterns["p_8_4_1_0_0"]    =  ("p_8_4_1_0_0",     8,4,1,0,0,1)
AllPatterns["p_6_2_1_2_2"]    =  ("p_6_2_1_2_2",     6,2,1,2,2,1)
AllPatterns["p_4_1_0_4_2"]    =  ("p_4_1_0_4_2",     4,1,0,4,2,1)
#AllPatterns["p_8_2_1_0_0"]    =  ("p_8_2_1_0_0",    8,2,1,0,0,?)
AllPatterns["p_9_9_1_0_0"]    =  ("p_9_9_1_0_0",     9,9,1,0,0,1)
AllPatterns["p_9_3_1_0_0"]    =  ("p_9_3_1_0_0",     9,3,1,0,0,1)
AllPatterns["p_10_10_1_0_0"]  =  ("p_10_10_1_0_0",   10,10,1,0,0,1)
AllPatterns["p_10_5_1_0_0"]   =  ("p_10_5_1_0_0",    10,5,1,0,0,1)
AllPatterns["p_6_2_1_4_2"]    =  ("p_6_2_1_4_2",     6,2,1,4,2,1)
AllPatterns["p_11_11_1_0_0"]  =  ("p_11_11_1_0_0",   11,11,1,0,0,1)
AllPatterns["p_12_12_1_0_0"]  =  ("p_12_12_1_0_0",   12,12,1,0,0,1)
AllPatterns["p_12_6_1_0_0"]   =  ("p_12_6_1_0_0",    12,6,1,0,0,1)
AllPatterns["p_12_4_1_0_0"]   =  ("p_12_4_1_0_0",    12,4,1,0,0,1)
AllPatterns["p_9_3_1_3_3"]    =  ("p_9_3_1_3_3",     9,3,1,3,3,1)
#AllPatterns["p_12_3_0_0_0"]   =  ("p_12_3_0_0_0",   12,3,0,0,0,?)
#AllPatterns["p_8_2_0_4_4"]    =  ("p_8_2_0_4_4",    8,2,0,4,4,?)
AllPatterns["p_14_7_1_0_0"]   =  ("p_14_7_1_0_0",    14,7,1,0,0,1)
AllPatterns["p_15_5_1_0_0"]   =  ("p_15_5_1_0_0",    15,5,1,0,0,1)
AllPatterns["p_9_3_1_6_3"]    =  ("p_9_3_1_6_3",     9,3,1,6,3,1)
AllPatterns["p_16_8_1_0_0"]   =  ("p_16_8_1_0_0",    16,8,1,0,0,1)
AllPatterns["p_12_4_1_4_4"]   =  ("p_12_4_1_4_4",    12,4,1,4,4,1)
#AllPatterns["p_16_4_0_0_0"]   =  ("p_16_4_0_0_0",   16,4,0,0,0,?)
#AllPatterns["p_8_2_0_8_4"]    =  ("p_8_2_0_8_4",    8,2,0,8,4,?)
AllPatterns["p_18_9_1_0_0"]   =  ("p_18_9_1_0_0",    18,9,1,0,0,1)
AllPatterns["p_18_6_1_0_0"]   =  ("p_18_6_1_0_0",    18,6,1,0,0,1)
#AllPatterns["p_12_3_0_6_6"]   =  ("p_12_3_0_6_6",   12,3,0,6,6,?)
AllPatterns["p_20_10_1_0_0"]  =  ("p_20_10_1_0_0",   20,10,1,0,0,1)
AllPatterns["p_15_5_1_5_5"]   =  ("p_15_5_1_5_5",    15,5,1,5,5,1)
#AllPatterns["p_20_5_0_0_0"]   =  ("p_20_5_0_0_0_0", 20,5,0,0,0,?)
AllPatterns["p_12_4_1_8_4"]   =  ("p_12_4_1_8_4",    12,4,1,8,4,1)





