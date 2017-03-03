#!/usr/bin/env python
"""
TravisCI manipulation utility class.
"""
# pylint: disable=unused-argument
from __future__ import print_function
import base64
import os
import time
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from apikit import BackendError


class TravisCI(object):
    """TravisCI represents an object presenting methods to facilitate
    TravisCI interactions from Python."""

    # Module static constants.
    travis_host = "https://api.travis-ci.org"
    # User-Agent must start with the string "Travis".
    # This is not documented by Travis CI and indeed the documentation
    #  states otherwise.  Nevertheless, it appears to be true.
    travis_headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.travis-ci.2+json",
        "User-Agent": "TravisLSSTAPI/0.1.0"
    }

    github_token = None
    travis_token = None
    public_keys = {}

    def __init__(self, github_token=None, travis_token=None):
        self.github_token = github_token
        if travis_token:
            self.travis_token = travis_token
        else:
            self.travis_token = self.exchange_token()
        self.travis_headers["Authorization"] = "token " + self.travis_token
        # Check authentication and fail if it doesn't work.
        req = requests.get(self.travis_host + "/", headers=self.travis_headers)
        self.raise_from_req(req)

    # pylint: disable=no-self-use
    def _debug(self, *args):
        """Super-cheesy way to get debugging output.
        """
        if os.environ.get("DEBUG"):
            print("DEBUG:", *args)

    # pylint: disable=no-self-use
    def raise_ise(self, text):
        """Turn error text into a BackendError Internal Server Error.  Handy
        for reraising exceptions in an easy-to-consume-by-the-client form.
        """
        if isinstance(text, Exception):
            # Just in case we are exuberantly passed the entire Exception and
            #  not its textual representation.
            text = str(text)
        raise BackendError(status_code=500,
                           reason="Internal Server Error",
                           content=text)

    # pylint: disable=no-self-use
    def raise_from_req(self, req):
        """Turn a failed request response into a BackendError.  Handy for
        reflecting HTTP errors from farther back in the call chain.
        """
        if req.status_code < 400:
            # Request was successful.  Or at least, not a failure.
            return
        raise BackendError(status_code=req.status_code,
                           reason=req.reason,
                           content=req.text)

    def exchange_token(self):
        """Exchange a GitHub token for a TravisCI one.
        """
        travis_token_url = self.travis_host + "/auth/github"
        postdata = {
            "github_token": self.github_token
        }
        self._debug("Exchanging GitHub token for Travis CI token")
        req = requests.post(travis_token_url, headers=self.travis_headers,
                            json=postdata)
        self.raise_from_req(req)
        # pylint: disable=broad-except
        try:
            rdata = req.json()
        except Exception as exc:
            self.raise_ise(str(exc))
        access_token = rdata.get("access_token")
        if not access_token:
            raise BackendError(status_code=403,
                               reason="Forbidden",
                               content="Unable to get Travis CI access token")
        self._debug("Travis CI token acquired")
        return access_token

    def start_travis_sync(self):
        """Initiate a Travis <-> GH Sync"""
        sync_url = self.travis_host + "/users/sync"
        # Start sync
        req = requests.post(sync_url, headers=self.travis_headers)
        if req.status_code == 409:
            # 409 is "already syncing"; so we pretend it was ours.
            req.status_code = 200
        self.raise_from_req(req)
        self._debug("Travis CI <-> GitHub Sync started")

    def enable_travis_webhook(self, slug):
        """Enable repository for Travis CI.
        """
        self.set_travis_webhook(slug, enabled=True)

    def disable_travis_webhook(self, slug):
        """Disable repository for Travis CI.
        """
        self.set_travis_webhook(slug, enabled=False)

    def set_travis_webhook(self, slug, enabled=True):
        """Enable/disable repository for Travis CI.
        """
        # pylint: disable=too-many-locals
        self.start_travis_sync()
        user_url = self.travis_host + "/repos/" + slug
        req = self._retry_request("get", user_url,
                                  headers=self.travis_headers)
        # Get the ID and flip the switch
        # pylint: disable=broad-except
        try:
            repo_id = req.json()["repo"]["id"]
        except Exception as exc:
            self.raise_ise(str(exc))
        self._debug("GitHub Repository ID: %s" % repo_id)
        hook_url = self.travis_host + "/hooks"
        hook = {
            "hook": {
                "id": repo_id,
                "active": enabled
            }
        }
        self._debug("Webhook payload:", hook)
        req = self._retry_request("put", hook_url, headers=self.travis_headers,
                                  payload=hook)
        self.raise_from_req(req)

    # pylint: disable = too-many-arguments
    def _retry_request(self, method, url, headers=None, payload=None,
                       auth=None, tries=10, initial_interval=5):
        """Retry an HTTP request with linear backoff.
        """
        self._debug("Beginning to wait for request %s %s" % (method, url))
        method = method.lower()
        attempt = 1
        while True:
            if method == "get":
                req = requests.get(url, params=payload, headers=headers,
                                   auth=auth)
            elif method == "put":
                req = requests.put(url, json=payload, headers=headers,
                                   auth=auth)
            elif method == "post":
                req = requests.post(url, json=payload, headers=headers,
                                    auth=auth)
            else:
                self.raise_ise("Bad method %s: must be 'get', 'put', "
                               "or 'post" % method)
            if req.status_code == 200:
                break
            self._debug("%s %s failed %d/%d" % (method, url,
                                                attempt, tries))
            errstr = "%d %s [%s]" % (req.status_code, req.reason, req.text)
            self._debug(errstr)
            delay = initial_interval * attempt
            if attempt == tries:
                rerrstr = "TravisCI request failed after %d tries: %s" \
                          % (tries, errstr)
                self.raise_ise(rerrstr)
            self._debug("Waiting %d seconds." % delay)
            time.sleep(delay)
            attempt += 1
        self._debug("Completed wait for request %s %s" % (method, url))
        return req

    def get_public_key(self, repo):
        """Retrieve public key from travis repo.
        """
        if repo in self.public_keys:
            return self.public_keys[repo]
        keyurl = self.travis_host + "/repos/%s/key" % repo
        # pylint: disable=broad-except, bad-continuation
        req = self._retry_request("get", keyurl, headers=self.travis_headers)
        self.raise_from_req(req)
        try:
            keyjson = req.json()
        except Exception as exc:
            self.raise_ise(str(exc))
        pubkey = keyjson.get("key")
        if pubkey:
            self.public_keys[repo] = pubkey
        return pubkey

    # Adapted from https://github.com/lsst-sqre/travis-encrypt
    # Forked from https://github.com/sivel/travis-encrypt
    # Thanks to Matt Martz
    def travis_encrypt(self, public_key, data):
        """Encrypt data with supplied public key.
        """
        key = RSA.importKey(public_key)
        cipher = PKCS1_v1_5.new(key)
        self._debug("Attempting encryption of string.")
        # Python 2/3
        try:
            bdata = bytes(data, "utf8")
        except TypeError:
            bdata = bytes(data)
        retval = base64.b64encode(cipher.encrypt(bdata)).decode("utf8")
        self._debug("Encryption succeeded.")
        return retval

    def create_travis_secure_string(self, public_key, data):
        """Create encrypted entry for travis.yml from data and key.
        """
        encstring = self.travis_encrypt(public_key, data)
        return "secure: \"%s\"" % encstring

    def travis_encrypt_for_repo(self, repo, data):
        """Encrypt data with public key for supplied repo name.
        """
        pubkey = self.get_public_key(repo)
        return self.travis_encrypt(pubkey, data)

    # pylint: disable=invalid-name
    def create_travis_secure_string_for_repo(self, repo, data):
        """Create encrypted entry for travis.yml from data and repo name.
        """
        pubkey = self.get_public_key(repo)
        return self.create_travis_secure_string(pubkey, data)
