#!/bin/python
import random
import math
import roomai

class KuhnPokerActions:
    bet   = 0;
    cheat = 1;

class KuhnPokerEnv(roomai.AbstractEnv):
    def __init__(self):
        self.validActions = [KuhnPokerActions(), KuhnPokerActions()]

    def init(self,players):

        if len(players) != 2:
            raise Exception("KuhnPoker is a game with two players.")
        

        self.player0_card = math.floor(random.random() * 3)
        self.player1_card = math.floor(random.random() * 3)
        while self.player1_card == self.player0_card:
            self.player1_card = math.floor(random.random() * 3)
        
        self.turn          = int(math.floor(random.random() * 2))
        self.firstPlayer   = self.turn
        self.actionHistory = [];

        self.initInfo                        = [dict(),dict(), dict()]; #the last one is used for chance player
        self.initInfo[0]["card"]             = self.player0_card
        self.initInfo[1]["card"]             = self.player1_card
        self.initInfo[self.turn]["order"]    = 0;
        self.initInfo[1- self.turn]["order"] = 1;
        self.initInfo[0]["id"]               = 0;
        self.initInfo[1]["id"]               = 1;
        self.initInfo[2]["turn"]             = [self.turn]
        self.initInfo[2]["firstTurnPlayer_card"]  = self.player0_card
        self.initInfo[2]["secondTurnPlayer_card"] = self.player1_card

        return False, [], self.initInfo, self.validActions

    def round(self,players):
        infoHistory = [];

        for player in players:
            player.reset()

        isTerminal, scores, Infos, ValidActions\
        = self.init(players)
        infoHistory.append(Infos);

        for i in xrange(len(players)):
            players[i].receiveValidActions(ValidActions[i]);
            players[i].receiveInformation(Infos[i]);

        while isTerminal == False:
            turn = Infos[2]["turn"]
            action = players[turn].takeAction()

            isTerminal, scores, Infos, ValidActions \
            = self.forward(action);
            infoHistory.append(Infos)

            for player in players:
                if isTerminal == False:
                    player.receiveInformation(Infos[i])
                else:
                    player.receiveResult(scores)

        return infoHistory, scores 

    def forward(self, action):
        self.actionHistory.append(actions)
        self.turn = 1 - self.turn

        info = [dict(), dict(), dict()] #the last one is used for the chance player
        info[0]["action"] = actions
        info[1]["action"] = actions
        info[2]["turn"]   = self.turn

        if len(self.actionHistory) == 1:
            return False, [], info, self.validActions;

        elif len(self.actionHistory) == 2:
            scores = self.evaluteTwo();
            if scores[0] != -1:
                return True,  scores, info, self.validActions
            else:
                self.turn = 1 - self.turn
                return False, scores, info, self.validActions

        elif len(self.actionHistory) == 3:
            scores = self.evaluateThree();
            return True, scores, info, self.validActions

        else:
            raise Exception("KuhnPoker has 3 turns at most. However len(self.actionHistory) = %d"%(len(self.actionHistory)))

    def backward(self):
        if len(self.actionHistory) == 1:
            self.actionHistory.pop()
            return True, [], self.InitInfo, self.validActions
        else:
            self.actionHistory.pop()
            self.turn = 1 - self.turn
            info = [dict(), dict()]
            info[0]["action"] = self.actionHistory[len(self.actionHistory)-1]
            info[1]["action"] = self.actionHistory[len(self.actionHistory)-1]
            info[2]["turn"]   = self.turn
            return False,[], info, self.validActions
    

    def WhoHasHigherCard(self):
        firstPlayer_card  = self.initInfo[self.firstPlayer]["card"]
        secondPlayer_card = self.initInfo[1-self.firstPlayer]["card"]

        if firstPlayer_card > secondPlayer_card:     return self.firstPlayer
        elif firstPlayer_card < secondPlayer_card:  return 1-self.firstPlayer
        else:   raise Exception("fuck")

    def evaluteTwo(self):
        win    = self.WhoHasHigherCard()
        scores = [0, 0];
        
        if self.actionHistory[0] == KuhnPokerActions.cheat and \
           self.actionHistory[1] == KuhnPokerActions.bet:
            return [-1,-1]
        
        if self.actionHistory[0] == self.actionHistory[1] and \
           self.actionHistory[0] == KuhnPokerActions.cheat:
            scores[win] = 1;
            return scores;

        if self.actionHistory[0] == KuhnPokerActions.bet and \
           self.actionHistory[1] == KuhnPokerActions.cheat:
            scores[self.firstPlayer] = 1;
            return scores;

        if self.actionHistory[0] == self.actionHistory[1] and \
           self.actionHistory[0] == KuhnPokerActions.bet:
            scores[win] = 2
            return scores;


    def evaluteThree(self):
        win = self.WhoHasHigherCard()
        scores = [0, 0]
        if self.actionHistory[2] == KuhnPokerActions.cheat:
            scores[1 - self.firstPlayer] = 1;
        else:
            scores[win] = 2;
        return scores;
       
