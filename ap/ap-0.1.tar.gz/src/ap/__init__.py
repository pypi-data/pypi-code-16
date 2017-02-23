#!/usr/bin/env python

import argparse
import datetime
import json
import os
import os.path
import subprocess
import sys
import urllib

import botocore.session

CACHE_PATH = "~/.ap"
WARN_CREDENTIALS_BEFORE = datetime.timedelta(minutes=45)
REFRESH_CREDENTIALS_BEFORE = datetime.timedelta(minutes=15)

def main():
    parser = argparse.ArgumentParser(usage="%(prog)s PROFILE [--update] COMMAND")
    parser.add_argument("profile", choices=botocore.session.Session().available_profiles)
    parser.add_argument("--refresh", dest="force_refresh", action="store_true", default=False)
    args, command = parser.parse_known_args()
    profile = args.profile
    force_refresh = args.force_refresh

    cache_path = os.path.expanduser(CACHE_PATH)
    ensure_path_exists(cache_path)

    session = get_authed_session(profile, JSONFileCache(cache_path))

    refresh = force_refresh
    if not refresh:
        credentials = session.get_credentials()
        if credentials._expiry_time is not None:
            if REFRESH_CREDENTIALS_BEFORE > credentials._expiry_time.replace(tzinfo=None) - datetime.datetime.utcnow():
                refresh = True

    if refresh:
        session = get_authed_session(profile, WriteOnlyJSONFileCache(cache_path))

    region = session.get_config_variable("region")
    os.environ["AWS_ACCESS_KEY_ID"] = credentials.access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.secret_key
    os.environ["AWS_SECURITY_TOKEN"] = credentials.token
    if region:
        os.environ["AWS_DEFAULT_REGION"] = region

    if credentials._expiry_time is not None:
        remaining = credentials._expiry_time.replace(tzinfo=None) - datetime.datetime.utcnow()
        if WARN_CREDENTIALS_BEFORE > remaining:
            remaining_minutes = int(remaining.total_seconds() / 60.0)
            sys.stderr.write((
                "> Credentials expire in {remaining_minutes} minutes.\n"
                "> Use \"{command} --refresh {profile} ...\" for an extra 60.\n"
                "\n"
            ).format(
                remaining_minutes=remaining_minutes,
                command=os.path.basename(sys.argv[0]),
                profile=profile
            ))
    sys.exit(subprocess.call(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr))

def get_authed_session(profile, cache):
    session = botocore.session.Session(profile=profile)

    cred_chain = session.get_component("credential_provider")
    cred_chain.get_provider("assume-role").cache = cache

    # Dummy API call to get credentials. Prompts for
    # MFA code if necessary.
    #session.create_client("iam").list_account_aliases()
    session.get_credentials()

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
        return os.path.join(self.path, urllib.quote(key, safe=""))

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
