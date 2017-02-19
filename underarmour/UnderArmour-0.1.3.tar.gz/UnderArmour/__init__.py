# -*- coding: utf-8 -*-
"""
Under Armour API Library
------------------
:license: MIT, see LICENSE for more details.
------------------
Usage
  from UnderArmour import UAOauth2Client, UA
  uaOauthObject = UAOauth2Client(client_id = ua_key, client_secret = ua_secret)
client_id, and client_secret are provided by Under Armour when registering your application
------------------
  url, state = uaOauthObject.authorize_token_url(ua_callback_url)
Let the user open the url. Save the state to the database
call_back_url is the url that you set when registering your app.
The user will be redirected to it after giving the app access to
their account. Under Armour will do a get request to that url
with a code. The code is used to get the token.
------------------
  tokenInfo = uaOauthObject.fetch_access_token(code)

tokenInfo contains all the info needed (access token, refresh token, etc.)
When getting the token info from Under Armour, save it to the database for later use.
------------------
  uaObject = UA(client_id = ua_key, client_secret = ua_secret, access_token=access_token)
Call the uaObject methods to interact with with Under Armour API.
Example:

  profile = uaObject.user_profile_get(user_id=ua_user_id)
------------------
For any methods that are not included in the library:

  result = uaObject.make_request(url, method, data)

The methods and data format could be found at:
https://developer.underarmour.com/docs/

"""
from .Exceptions import *
from .UnderArmour import UA, UAOauth2Client
# Meta info
__version__ = "0.1.3"
__author__ = "Igor Fala"
__license__ = 'MIT'
