# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
Helpers for making an API call
"""
from builtins import str
from collections import OrderedDict
import json
import logging
import requests
import sys
import os

from ncloud.formatting.output import print_error
from ncloud import __version__

logger = logging.getLogger()


def print_debug(res):
    print("b%r" % res.content)
    print("%r" % res.text)
    print("%r" % res.encoding)
    print("%r" % res.headers)
    print("%r" % res.ok)
    print("%r" % res.reason)
    print("%r" % res.status_code)
    print('')


def api_call(config, endpoint, method="GET", data=None,
             params=None, files=None, headers={}, stream=False, session=None,
             return_status_code=False, token_needed=True,
             console_log_follow=False, add_ncloud_data=True):
    # if we have console_log_follow, then don't do a sys.exit() despite
    # having no results to show yet
    if add_ncloud_data:
        sys.argv[0] = 'ncloud'
        ncloud_data = {
            'ncloud_cmd': ' '.join(sys.argv),
            'ncloud_version': __version__
        }
        if params:
            params.update(ncloud_data)
        else:
            params = ncloud_data

    url = config.api_url() + endpoint
    if token_needed:
        token = config.get_token(refresh=False)
    else:
        token = "no token needed"

    try:
        headers["Authorization"] = "Bearer " + token

        # check if we are keeping all api calls within the same session
        # this ensures that keep-alive is true
        if session:
            req = requests.Request(method, url, data=data, headers=headers,
                                   params=params, files=files)
            prepped = session.prepare_request(req)
            res = session.send(prepped, stream=stream)
        else:
            res = requests.request(method, url, data=data, params=params,
                                   files=files, headers=headers, stream=stream)
        # used in formatting new tests (add the data to a new txt file
        # in the test_system folder); ex: export DEBUG=1; ncloud m l -t 0
        if os.environ.get('DEBUG', '') == '1':
            print_debug(res)

        if res.status_code == 401:
            # token authentication failed, try to generate a new one and retry
            token = config.get_token(refresh=True)

            if session:
                # if we are keeping the api_call inside of a session
                prepped.headers["Authorization"] = "Bearer " + token
                res = session.send(prepped, stream=stream)
            else:
                headers["Authorization"] = "Bearer " + token
                res = requests.request(method, url, data=data, params=params,
                                       files=files, headers=headers,
                                       stream=stream)
        elif not str(res.status_code).startswith('2'):
            # if we are logging immediately, then we might not have
            # log files yet, in which case don't print that out and then exit
            print_error(res) if not console_log_follow else ''
    except requests.exceptions.ConnectionError:
        logger.error("Unable to connect to server.")
        sys.exit(1)
    except requests.exceptions.RequestException as re:
        logger.error(re)
        sys.exit(1)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    if res is not None:
        content_type = res.headers['content-type']

        if content_type == 'application/json':
            return res.text if not return_status_code else \
                (res.text, res.status_code)
        else:
            # TODO: helium doesn't appear to set 'application/json' correctly
            if stream:
                return res if not return_status_code else \
                    (res, res.status_code)
            elif res.encoding:
                return res.content.decode(res.encoding) \
                    if not return_status_code else \
                    (res.content.decode(res.encoding), res.status_code)
            else:
                return res.content if not return_status_code else \
                    (res.content, res.status_code)
    else:
        logger.error("No response received. Exiting.")
        sys.exit(1)


def api_call_json(config, endpoint, method="GET", data=None,
                  params=None, files=None, token_needed=True, headers={},
                  add_ncloud_data=True):
    response = api_call(config, endpoint, method, data, params,
                        files, headers, token_needed=token_needed,
                        add_ncloud_data=add_ncloud_data)
    return json.loads(response, object_pairs_hook=OrderedDict)
