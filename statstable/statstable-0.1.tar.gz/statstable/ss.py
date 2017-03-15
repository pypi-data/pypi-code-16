import requests
import time
import datetime

# Global variables
__vars = {
    'apiKey': None, # Used in Authentication header
    'apiUrl': 'https://api.statstable.com/v1/',
    'authenticated': False, # Prevent multiple authentications
    'apiRate': 1, # Prevents flooding of server
    'lastRequestTime': None # Prevent flooding of server
}

# Make a request to the API
def __getResource(resource, parameters=None):
    global __vars

    parameters = parameters or {}

    if resource!='' and not __vars['authenticated']:
        if not authenticate(None):
            return {'error': 'API key is invalid'}

    curTime = datetime.datetime.now()
    if __vars['lastRequestTime'] is not None:
        timeBetweenRequests = 1.0 / __vars['apiRate']
        timeSinceLastRequest = (curTime - __vars['lastRequestTime']).total_seconds()
        waitTime = max(0, timeBetweenRequests - timeSinceLastRequest)
        if waitTime > 0: time.sleep(waitTime)

    headers = {
        'Authorization': __vars['apiKey'],
        'Content-Type': 'application/json'
    }

    for k,v in parameters.iteritems():
        if type(v) is list:
            parameters[k] = ','.join(v)

    __vars['lastRequestTime'] = datetime.datetime.now()
    r = requests.get(__vars['apiUrl'] + resource, headers=headers, params=parameters)
    if r.headers['x-api-rate']:
        __vars['apiRate'] = float(r.headers['x-api-rate'])

    if r.status_code==200:
        try:
            return r.json()
        except:
            return {}
    elif r.status_code==429:
        return __getResource(resource, parameters)
    else:
        try:
            return {'error': r.json()}
        except:
            return {
                'error': { 
                    'message':r.text,
                    'code': r.status_code
                }
            }

def authenticate(apiKey):
    global __vars
    __vars['apiKey'] = apiKey
    r = __getResource('', {})
    if 'error' in r: 
        return False
    else: 
        __vars['authenticated'] = True
        return True

def getNBAPlayers(params=None): return __getResource('nba/players', params)
def getNBAGames(params=None): return __getResource('nba/games', params)
def getNBATeams(params=None): return __getResource('nba/teams', params)
def getNBAStats(params=None): return __getResource('nba/stats', params)
