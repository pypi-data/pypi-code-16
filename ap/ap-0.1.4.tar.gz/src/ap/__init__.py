#!/usr/bin/env python

import argparse
import datetime
import json
import os
import os.path
import subprocess
import sys

try:
    # Python 2
    from urllib import quote as urllib_quote
except ImportError:
    # Python 3
    from urllib.parse import quote as urllib_quote

import botocore.session

CACHE_PATH = "~/.ap"

def main():
    # Parse args.
    parser = argparse.ArgumentParser(usage="%(prog)s PROFILE [--cached] COMMAND")
    parser.add_argument("profile", choices=botocore.session.Session().available_profiles)
    parser.add_argument("--cached", dest="read_credentials_from_cache", action="store_true", default=False, help="Use cached credentials")
    args, command = parser.parse_known_args()
    profile = args.profile
    read_credentials_from_cache = args.read_credentials_from_cache

    # Setup cache. If --cached isn't passed, use a write-only cache so we
    # at least store credentials for future --cached calls.
    cache_path = os.path.expanduser(CACHE_PATH)
    ensure_path_exists(cache_path)
    if read_credentials_from_cache:
        cache = JSONFileCache(cache_path)
    else:
        cache = WriteOnlyJSONFileCache(cache_path)
    
    # Start a session, fetching credentials if necessary.
    session = get_authed_session(profile, cache)

    # Populate subprocess environment variables.
    credentials = session.get_credentials()
    region = session.get_config_variable("region")
    os.environ["AWS_ACCESS_KEY_ID"] = credentials.access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.secret_key
    os.environ["AWS_SECURITY_TOKEN"] = credentials.token
    if region:
        os.environ["AWS_DEFAULT_REGION"] = region

    # If using cache, show how long credentials will last.
    if read_credentials_from_cache and credentials._expiry_time is not None:
        remaining = credentials._expiry_time.replace(tzinfo=None) - datetime.datetime.utcnow()
        remaining_minutes = int(remaining.total_seconds() / 60.0)
        sys.stderr.write("Cached credentials expire in {remaining_minutes} minutes.\n\n".format(remaining_minutes=remaining_minutes))
    
    sys.exit(subprocess.call(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr))

def get_authed_session(profile, cache):
    session = botocore.session.Session(profile=profile)
    cred_chain = session.get_component("credential_provider")
    cred_chain.get_provider("assume-role").cache = cache
    session.get_credentials() # Fetch credentials from cache, config or API.
    return session

def ensure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

class JSONFileCacheMixin(object):
    def __init__(self, path):
        self.path = path

    def _get_key_filename(self, key):
        return os.path.join(self.path, urllib_quote(key, safe=""))

class ReadJSONFileCacheMixin(JSONFileCacheMixin):
    def __getitem__(self, key):
        filename = self._get_key_filename(key)
        try:
            with open(filename) as fp:
                return json.load(fp)
        except IOError:
            if os.path.isfile(filename):
                raise
            else:
                raise KeyError

class WriteJSONFileCacheMixin(JSONFileCacheMixin):
    def __setitem__(self, key, value):
        def json_default(obj):
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                raise TypeError
        encoded = json.dumps(value, default=json_default)
        with open(self._get_key_filename(key), "w") as fp:
            fp.write(encoded)

class JSONFileCache(ReadJSONFileCacheMixin, WriteJSONFileCacheMixin):
    pass

class WriteOnlyJSONFileCache(WriteJSONFileCacheMixin):
    def __getitem__(self, key):
        raise KeyError

if __name__ == "__main__":
    main()
