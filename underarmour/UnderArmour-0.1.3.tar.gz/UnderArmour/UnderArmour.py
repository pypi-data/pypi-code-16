try:
    from urllib.parse import urlencode
except ImportError:
    # Python 2.x
    from urllib import urlencode

from requests_oauthlib import  OAuth2Session
from UnderArmour.Exceptions import *
import datetime, json, requests
class UAOauth2Client(object):
    API_VERSION = 7.1
    API_ENDPOINT = "https://api.ua.com"
    AUTHORIZE_ENDPOINT = "https://www.mapmyfitness.com/v{0}/oauth2/uacf/authorize/?".format(API_VERSION)
    TOKEN_ENDPOINT = 'https://api.mapmyfitness.com/v{0}/oauth2/access_token/'.format(API_VERSION)


    def __init__(self, client_id, client_secret,
                 access_token=None, refresh_token=None,
                 *args, **kwargs):
        """
        Create a UAOauth2Client object. Specify just the first 2 parameters
        to start the setup for user authorization.
            - client_id, client_secret are in the app configuration page
            https://developer.underarmour.com/apps/
            - access_token, refresh_token are obtained after the user grants permission
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.token = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def make_request(self, url, data=None, method=None, **kwargs):
        """
        Builds and makes the OAuth2 Request, catches errors
        """
        if data == None:
            data = {}
        if not method:
            method = 'post' if data else 'get'
        headers = {"Authorization": "Bearer {0}".format(self.token.get('access_token')),
                   'Api-Key': self.client_id,
                   "Content-Type": "application/json"}
        try:
            if method == 'get':
                response = getattr(requests, method)(url=url, headers=headers)
            else:
                response = getattr(requests, method)(url=url, headers=headers, data=data)
        except HTTP_401_UNAUTHORIZED as e:
            # Check if needs_refresh in response,
            #then refresh token from outside and try again.
            response = {'needs_refresh': 'Please refresh the token'}

        if response.status_code == 401:
            raise HTTP_401_UNAUTHORIZED(response.json())
        elif response.status_code == 403:
            raise HTTP_403_FORBIDDEN(response.json())
        elif response.status_code == 404:
            raise HTTP_404_NOT_FOUND(response.json())
        elif response.status_code == 405:
            raise HTTP_405_METHOD_NOT_ALLOWED(response.json())
        elif response.status_code >= 500:
            raise HTTP_500_INTERNAL_SERVER_ERROR(response.json())
        return response.json()

    def authorize_token_url(self, redirect_uri=None, **kwargs):
        """Step 1: Return the URL the user needs to go to in order to grant us
        authorization to look at their data.  Then redirect the user to that
        URL, open their browser to it, or tell them to copy the URL into their
        browser.
            - redirect_uri: url to which the response will posted
                            required only if your app does not have one
            for more info see https://developer.underarmour.com/docs/v71_OAuth_2_Intro
        The method returns a tuple: (URL, state). It is a good idea to save state to
        the database, so the user is later identfied by the state in the next steps.
        """

        params = {"redirect_uri": redirect_uri}
        authorization_url = "%s%s" % (self.AUTHORIZE_ENDPOINT, urlencode(params))
        oauth = OAuth2Session(self.client_id) # creating session
        out = oauth.authorization_url(authorization_url, **kwargs)

        return(out)

    def fetch_access_token(self, code):

        """Step 2: Given the code from Under Armour from step 1, it calls
        Under Armour again and returns an access token object. Extract the needed
        information from that and save it to use in future API calls.
        the token is internally saved.
        """
        client_auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        post_data = { "code": code,
                 "grant_type": "authorization_code",
                 }

        response = requests.post(self.TOKEN_ENDPOINT,
                             auth=client_auth,
                             data=post_data
                             )
        token_json = response.json()
        return token_json

    def refresh_token(self):
        """Step 3: obtains a new access_token from the the refresh token
        obtained in step 2.
        the token is internally saved
        """
        client_auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        post_data = { "refresh_token": self.token.get('refresh_token'),
                      "grant_type": "refresh_token"}
        response = requests.post(self.TOKEN_ENDPOINT,
                             auth=client_auth,
                             data=post_data)
        token_json = response.json()
        return token_json

class UA(object):

    API_ENDPOINT = "https://api.ua.com"
    def __init__(self, client_id, client_secret, access_token=None,  refresh_token=None, **kwargs):
        """
        UA(<id>, <secret>, access_token=<token>, refresh_token=<token>)
        """
        self.client = UAOauth2Client(client_id, client_secret, access_token=access_token, refresh_token=refresh_token, **kwargs)

    def make_request(self, url, method=None, data = None, *args, **kwargs):
        # This handles data level errors, improper requests, and bad
        # serialization
        response = self.client.make_request(url, data, method, *args, **kwargs)
        return response

    def user_profile_get(self, user_id=None):
        """
        Get a user profile. You can get other user's profile information
        by passing user_id, or you can get the current user's by not passing
        a user_id
        https://developer.underarmour.com/docs/v71_User

        If no user is passed to function, it will automatically
        retrieve the info for current user
         """
        if user_id == None:
            user_id = 'self'
        url = '{0}/v7.1/user/{1}/'.format(self.API_ENDPOINT, user_id)
        return self.make_request(url)

    def user_profile_update(self, user_id=None, data=None):
        """
        Set a user profile. You can set your user profile information by
        passing a dictionary of attributes that will be updated.
        https://developer.underarmour.com/docs/v71_User
        """
        if user_id == None:
            user_id = 'self'
        url = '{0}/v7.1/user/{1}/'.format(self.API_ENDPOINT, user_id)
        return self.make_request(url, method='put', data=data)

    def privacy_options(self, user_id=None):
        """
        See all privacy options for the given user.
        If no user is passed in, than reqular privacy options
        are passed in.
        DOCS:
        https://developer.underarmour.com/docs/v71_User_Profile_Photo
        """
        if user_id == None:
            user_id = ''
        url = '{0}/v7.1/privacy_option/{1}/'.format(self.API_ENDPOINT, user_id)
        return self.make_request(url)
