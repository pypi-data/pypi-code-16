# oopyconnector : python framework for connecting to the Only Once API
#
#
# Author(s)     :   - Henri Kuiper (henri.kuiper@onlyonce.com)

#
#
# Version       : 2.0beta

import requests
import datetime
import threading
import time




def is_paginated(response_json):
    return not response_json['last']






class OOCardParser():
    '''Helper class for parsing of cards
    '''

    def findField(self, field, model):
        '''Finds a field within a card or returns None
        Can also return "wrappers" (like jobs_group_wrapper)
        '''
        if model.has_key('definitionName'):
            if model['definitionName'] == field:
                flds = field.split('_')
                if flds[len(flds)-1] == 'wrapper':
                    return model['components']
                else:
                    return model['value']
        if model.has_key('components'):
            for item in model['components']:
                val = self.findField(field, item)
                if val != None:
                    return val
        else:
            return None

    def getInfo(self, card, fields):
        '''Retrieves all fields from a card. Fields should be speicifed as a list of 'strings'.
        '''
        res = {}
        for field in fields:
            res[field] = self.findField(field, card['model'][0])
        return res

    def basicInfo(self, card):
        '''Primed call to 'getInfo'. Returns a JSON :
        {'first_name_field': '......',
         'middle_name_field': '.....',
         'last_name_field': '......',
         'mobile_number': '......',
         'email' : '.......'
        }
        '''
        fields = ['first_name_field', 'middle_name_field', 'last_name_field', 'communication_mobtel1_field', 'communication_email1_field']
        return self.getInfo(card, fields)

class OO():

    apibase = ""

    baseurl  = "http://apiteststand.onlyonce.com"
    version  = "v2"

    seckey   = None
    apisec   = None
    apikey   = None

    username = None
    password = None

    bearer   = None

    maxThreadCount = 30
    network  = []
    cardsReceived = []
    virtualCards = []

    lastCardSync = None
    profileAccessEnabled = False

    random_names = {}

    def signin(self):
        if not self.username:
            raise Exception, "Cannot signin without your username"
        if not self.password:
            raise Exception, "Cannot signin without your password"

        self.apibase = self.baseurl + "/" + self.version
        payload = "{\"username\" : \"" + self.username + "\",\n \"password\" : \"" + self.password + "\"\n}"
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", self.apibase + "/signIn", data=payload, headers=headers)
        if response.status_code != 200:
            raise Exception, "Faulty Signin"
        self.bearer = response.headers['Authorization']
        return True

    def signout(self):
        '''Returns public card for a profile'''
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'Authorization': self.bearer
        }
        response = requests.request("GET", self.apibase + "/signOut", headers=headers)
        print "SIGNOUT: %s" % response


    def datastore(self, profile=None):
        '''return it, if there is a profile'''
        self.getAccess(profile)
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'Authorization': self.bearer
        }
        response = requests.request("GET", self.apibase + "/profiles/%s/dataStore" % profile, headers=headers)
        return response.json()

    def profile(self, profileid):
        '''Returns public card for a profile'''
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'Authorization': self.bearer
        }
        response = requests.request("GET", self.apibase + "/profiles/%s" % profileid, headers=headers)
        return response.json()

    def profiles(self,scope='MINE'):
        '''Return profiles
        scope = MINE (Default) All profiles owned by the authenitcated user
        scope = BOOKMARKS All bookmarked profiles
        scope = CONNECTIONS All profiles sharing data with, or receiving data from
        '''

        if not self.bearer:
            raise Exception, "No bearer token present, use signin first"
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'Authorization': self.bearer
        }

        res = []
        response = requests.request("GET", self.apibase + "/profiles?scope=%s" % scope, headers=headers)
        for p in response.json()['content']:
            profile = {}
            profile['name'] = p['name']
            profile['id'] = p['id']
            profile['ooid'] = p['onlyonceId']
            profile['type'] = p['type']
            profile['inc'] = p['incomingSharesCount']
            profile['out'] = p['outgoingSharesCount']
            if profile['inc'] > profile['out']:
                profile['kind'] = 'CONSUMER'
            else:
                profile['kind'] = 'PROVIDER'
            res.append(profile)
        return res



    def connect(self):
        self.apibase  = self.baseurl + "/" +  self.version
        if not self.bearer:
            raise Exception, "No bearer token present, use register first"


    def cardsAge(self):
        '''Returns time since last cards-sync in seconds. Returns 9999 if no
        sync has been performed yet'''
        if lastCardSync == None:
            return 9999
        else:
            return (datetime.datetime.now() - lastCardSync).seconds

    def getAccess(self, profile=None):
        '''Some endpoints require acccess. Access is granted if this endpoint is hit with a correct secret key for the
        accompanying profile.
        '''
        if not self.seckey:
            raise Exception, "You need to provide your secret key for us to enable access to your encrypted data"
        if not profile:
            raise Exception, "You need to specify a profile"
        headers = {
            'content-type': "application/json",
            'Authorization': self.bearer,
            'Secret-Key': self.seckey,
            'cache-control': "no-cache"
        }

        response = requests.request("POST", self.apibase + "/profiles/" + profile + "/access", headers=headers)

        if response.status_code == 200:
            self.profileAccessEnabled = True

        return True


    def cards(self, profile, scope='ACCEPTED', maxAge=60):
        self.apibase  = self.baseurl + "/" +  self.version
        '''Returns all cards shared with me. Saves API calls by not refreshing
        within maxAge seconds. To get own cards, set scope to MINE
        '''
        #TODO: When calling with different scope, make sure to always refresh. Or keep two caches!


        if self.cardsAge > maxAge:
            headers = {
                'content-type': "application/json",
                'Authorization': self.bearer,
                'cache-control': "no-cache"
            }

            response = requests.request("GET", self.apibase + "/profiles/" + profile + "/cards?scope=" + scope , headers=headers)
            j = response.json()
            if j['content']:
                all_cards = len(j['content'])
                page = 0
                # This may return a paginated respsonse....
                while all_cards < response.json()['total']:
                    page += 1
                    response = requests.request("GET", self.apibase + "/profiles/" + profile + "/cards?scope=" + scope + "&page=" + str(page), headers=headers)

                    for to_add in response.json()['content']:
                        j['content'].append(to_add)
                    all_cards += len(response.json()['content'])
                self.cardsReceived = []
                for card in j['content']:
                    c = {}
                    #TODO make this a call to lookup the card (and cache it)
                    c['owner'] = card['ownerId']
                    c['name'] = card['name']
                    c['id'] = card['id']
                    self.cardsReceived.append(c)
                self.lastCardSync = datetime.datetime.now()

        return self.cardsReceived

    def connections(self):
        '''Returns a list of all unique users who have shared data with you.
        Returns empty list if no data shared with you, or you have not called 'cards' yet
        '''
        connections = []
        for card in self.cardsReceived:
            if card['owner'] not in connections:
                connections.append(card['owner'])
        return connections



    def card(self, profileid, cardid):
        '''Returns the full card JSON'''

        if not self.profileAccessEnabled:
            self.getAccess(profileid)
        self.apibase  = self.baseurl + "/" +  self.version
        headers = {
            'content-type': "application/json",
            'authorization':  self.bearer,
            'cache-control': "no-cache"
            }

        response = requests.request("GET", self.apibase + "/profiles/" + profileid + "/cards/" + cardid, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception, "Cannot return card, decryption not possible. Secret-Key not sent via /access endpoint? API status=%s" % response.status_code

    def getRequests(self, profileid, reqtype=None, status=None):
        if not self.profileAccessEnabled:
            self.getAccess(profileid)
        self.apibase  = self.baseurl + "/" +  self.version
        headers = {
            'content-type': "application/json",
            'authorization':  self.bearer,
            'cache-control': "no-cache"
            }

        response = requests.request("GET", self.apibase + "/profiles/" + profileid + "/requests?&statuses=" + status + "&type=" + reqtype, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception, "Cannot return card-requests. API status=%s" % response.status_code


    def getVirtualCards(self, profileid, fields=['first_name_field', 'last_name_field'], onlyifall=False):
        '''Fills self.virtualCards with cards per network connection containing
        the fields as specified (default = firstName, lastName).

        These virtual cards look like this:
        { '324234-234234-234243234':
          {  'first_name_field'   : 'John',
             'last_name_field'    : 'Doe'
          },
          '4256774...
        }

        In order to do so, we get ALL the cards shared with the selected profile and
        decrypt those in a threaded (self.maxThreadCount threads) execution model.

        The result is then stored in self.virtualCards.

        This is 'condensed' as to contain only the requested fields per network connection.

        If 'onlyifall' is set to True any connections not sharing ALL FIELDS are dropped from the result.
        '''

        if self.cardsReceived == []:
            self.cards(profileid, scope='ACCEPTED')

        def readCardThread(cardid, cardname, profileid,  oo):
            print "Another Thread....."
            try:
                c = self.card(profileid, cardid)
            except:
                c = False     # to skip any decrypt/card-get errors :)
            if c:
                oo.virtualCards.append(c)

        self.getAccess(profileid) # for timing issues :)
        for card in self.cardsReceived:
            while threading.activeCount() > self.maxThreadCount:
                time.sleep(1)   # sleep it off lol. also fixes some timing issues :)
            threading.Thread(target=readCardThread, args=(card['id'], card['name'], profileid, self)).start()

        while threading.activeCount() > 1:
            time.sleep(1)   # make sure there are no more threads :)


        res = {}
        ocp = OOCardParser()
        for card in self.virtualCards:
            bad_card = False
            try:
                data = ocp.getInfo(card, fields)
            except:
                bad_card = True
            # For every field we have with data in the card, we add it to the global storage if it's not there already with that value
            if not res.has_key(card['ownerId']):
                '''If we have no virtual card for this connection, we create one :)
                '''
                res[card['ownerId']] = {}

            for field in fields:
                #TODO Fix naive implementation. This still not checks for other values (grouped fields issue!!!)
                if not res[card['ownerId']].has_key(field):
                    if not bad_card:
                        if data[field] != None:
                            res[card['ownerId']][field] = data[field]
                else:
                    if not bad_card:
                        if res[card['ownerId']][field] != data[field] and data[field] != None:
                                print "Eeek other value, fix this (%s <> %s)" % (res[card['ownerId']][field], data[field])


        if onlyifall:
            res2 = {}
            for conn in res:
                if len(fields) == len(res[conn]):
                    res2[conn] = res[conn]
            return res2
        else:
            return res


    def acceptRequest(self, requestID):
        if not self.profileAccessEnabled:
            self.getAccess(profileid)
        self.apibase  = self.baseurl + "/" +  self.version
        headers = {
            'content-type': "application/json",
            'authorization':  self.bearer,
            'cache-control': "no-cache"
            }
        data = {"ids":[requestID]}

        response = requests.request("GET", self.apibase + "/requests/accept", data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception, "Cannot return card-requests. API status=%s" % response.status_code

    def birthdaylist(self, profileid):
        '''Returns list of :
        {   'first_name_field' : 'John',
                                'last_name_field'  : 'Doe',
                                'date_of_birth'    : '1976-06-12'
        }


        This is is sorted on 'next upcoming' birthays (determined from today)
        '''

        if not self.bearer:
            raise Exception, "Cannot create birthdaylist, call signin() first."

        if not self.seckey:
            raise Exception, "Secret Key needed."

        self.getAccess(profileid)
        blist = []
        bdaycards = self.getVirtualCards(profileid, fields=['first_name_field', 'last_name_field', 'date_of_birth_field'], onlyifall=True)
        for bd in bdaycards:
            blist.append(bdaycards[bd])

        # we need to 'add' birthdate
        for bd in blist:
            dd = bd['date_of_birth_field'].split('-')
            bd['birthdate'] = dd[1] + "-" + dd[0]
        from operator import itemgetter
        upcoming = sorted(bd, key=itemgetter('birthdate'))

        import datetime
        today = datetime.date.today()
        lookfor = "%02d-%02d" % (today.month, today.day)

        n = []
        p = []

        for b in upcoming:
            if b['birthdate'] >= lookfor:
                n.append(b)
            else:
                p.append(b)
        for i in p:
            n.append(i)
        return n


