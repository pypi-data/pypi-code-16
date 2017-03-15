#!/usr/bin/env python
"""Construct a session authenticated through the Bitly OAuth2 Proxy"""

import requests


class Session(requests.Session):
    """Authenticated (via Bitly OAuth2 Proxy) HTTPS session"""

    oauth2_username = None
    _oauth2_password = None
    authentication_base_url = None
    authentication_session_url = None
    authentication_postdata = None

    def __init__(self, oauth2_username=None, oauth2_password=None,
                 authentication_base_url=None,
                 authentication_session_url=None,
                 authentication_postdata=None,
                 **kwargs):  # pylint: disable=too-many-arguments
        """Create a new authenticated session"""
        requests.Session.__init__(self, **kwargs)
        self.oauth2_username = oauth2_username
        self._oauth2_password = oauth2_password
        self.authentication_base_url = authentication_base_url
        self.authentication_session_url = authentication_session_url
        self.authentication_postdata = authentication_postdata
        if self.oauth2_username and self._oauth2_password and \
           self.authentication_base_url:
            self.authenticate()

    def set_oauth2_username(self, username):
        """Set the oauth username"""
        self.oauth2_username = username

    def set_oauth2_password(self, password):
        """Set the OAuth2 password"""
        self._oauth2_password = password

    def set_authentication_base_url(self, url):
        """Set the OAuth2 authentication base URL"""
        self.authentication_base_url = url

    def set_authentication_session_url(self, url):
        """Set the OAuth2 authentication session URL"""
        self.authentication_session_url = url

    def get_oauth2_username(self):
        """Return the OAuth2 username"""
        return self.oauth2_username

    def get_authentication_base_url(self):
        """Return the OAuth2 authentication base URL"""
        return self.authentication_base_url

    def get_authentication_session_url(self):
        """Return the OAuth2 authentication session URL"""
        return self.authentication_session_url

    def get_authentication_postdata(self):
        """Return the POST data for OAuth2 session authentication"""
        return self.authentication_postdata

    def authenticate(self):
        """Authenticate the session"""
        postdata = self.authentication_postdata
        jar = requests.cookies.cookielib.CookieJar()
        self.cookies = jar
        resp = self.get(self.authentication_base_url)
        authtok = _extract_authenticity_token(resp.content)
        if postdata is None:
            # This works for GitHub
            postdata = {"login": self.oauth2_username,
                        "password": self._oauth2_password,
                        "authenticity_token": authtok,
                        "commit": "Sign+in",
                        "utf8": u"\u2713",
                        }  # pylint: disable=bad-continuation
            self.authentication_postdata = postdata
        if self.authentication_session_url is None:
            # This is also for GitHub
            authentication_session_url = "https://github.com/session"
            self.authentication_session_url = authentication_session_url
        self.post(self.authentication_session_url, data=postdata)


def _extract_authenticity_token(data):
    """Don't look, I'm hideous!"""
    # Super-cheap Python3 hack.
    if not isinstance(data, str):
        data = str(data, 'utf-8')
    pos = data.find("authenticity_token")
    # Super-gross.
    authtok = str(data[pos + 41:pos + 41 + 88])
    return authtok
