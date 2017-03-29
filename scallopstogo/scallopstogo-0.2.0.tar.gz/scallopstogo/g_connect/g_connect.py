import json
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def get_google_service(storage, service_type, version_type):
    '''
    function takes json storage variable and returns calendar api connection
    ex. for calendar: service_type: calendar, version_type: v3
    '''

    # parse json from storage key
    storage = json.loads(storage.replace('\n', ''))

    access_token = storage['access_token']
    client_id = storage['client_id']
    client_secret = storage['client_secret']
    refresh_token = storage['refresh_token']
    expires_at = storage['token_response']['expires_in']
    user_agent = storage['user_agent']
    token_uri = storage['token_uri']

    # auth to google, this function will return a refresh token
    cred = client.GoogleCredentials(access_token, client_id, client_secret,
                                    refresh_token, expires_at, token_uri, user_agent,
                                    revoke_uri="https://accounts.google.com/o/oauth2/token")
    http = cred.authorize(Http())
    cred.refresh(http)
    service = build(service_type, version_type, credentials=cred)

    return service
