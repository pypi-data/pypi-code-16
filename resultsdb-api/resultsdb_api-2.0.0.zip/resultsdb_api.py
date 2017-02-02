# Copyright 2013, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author: Josef Skladanka <jskladan@redhat.com>

import requests
import json
import inspect
import simplejson
import logging

logger = logging.getLogger('resultsdb_api')
logger.addHandler(logging.NullHandler())

_KEEP = object()


def _fparams(expand_kwargs=True):
    """Gets the parameters of the function, from which _fparams is called
    and returns the list of params, minus `self`"""
    frame = inspect.currentframe().f_back
    args, varargs, keywords, values = inspect.getargvalues(frame)

    params = {}

    for key in args:
        if key == 'self':
            continue
        params[key] = values[key]

    if keywords:
        if expand_kwargs:
            for key, value in values[keywords].iteritems():
                params[key] = value
        else:
            params[keywords] = values[keywords]

    return params


class ResultsDBapiException(Exception):

    def __init__(self, message='', response=None):
        ''':param response: :class:`requests.Response` object'''
        self.message = message
        self.response = response

    def __str__(self):
        return repr(self.message)


class ResultsDBapi(object):

    def __init__(self, api_url):
        # remove trailing slash(es), so we don't generate
        # urls with a double slash which breaks werkzeug
        # https://github.com/mitsuhiko/werkzeug/issues/491
        self.url = api_url.rstrip('/')

    def __raise_on_error(self, r):
        if r.ok:
            return

        try:
            logger.warn('Received HTTP failure status code %s for request: %s',
                        r.status_code, r.url)
            raise ResultsDBapiException(
                '%s (HTTP %s)' % (r.json()['message'], r.status_code), r)
        except simplejson.JSONDecodeError as e:
            logger.debug('Received invalid JSON data: %s\n%s', e, r.text)
            raise ResultsDBapiException(
                'Invalid JSON (HTTP %s): %s' % (r.status_code, e), r)
        except KeyError:
            raise ResultsDBapiException('HTTP %s Error' % r.status_code, r)

    def __prepare_params(self, params_all):
        params = {}
        for key, value in params_all.iteritems():
            if value is None:
                continue
            if key == 'raw_params':
                continue

            # if a param's name ends with _like, we treat it as if :like filter should be applied
            #  for the rare case, where it really is supposed to be the name, user should provide
            #  it in the 'raw_params' dict
            if key.endswith('_like'):
                key = "%s:like" % key[:-len('_like')]

            if type(value) in (list, tuple):
                params[key] = ','.join([unicode(v) for v in value])
            else:
                params[key] = unicode(value)

        if 'raw_params' in params_all.keys() and params_all['raw_params']:
            raw_params = {
                key: unicode(value) for key, value in params_all['raw_params'].iteritems()}
            params.update(raw_params)
        return params

    def create_group(self, uuid=None, ref_url=None, description=None):
        url = "%s/groups" % self.url
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(_fparams()), headers=headers)
        self.__raise_on_error(r)

        return r.json()

    def update_group(self, uuid, ref_url=_KEEP, description=_KEEP):
        data = {}
        if ref_url is not _KEEP:
            data['ref_url'] = ref_url
        if description is not _KEEP:
            data['description'] = description
        if data:
            data['uuid'] = uuid

        url = "%s/groups" % self.url
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        self.__raise_on_error(r)

        return r.json()

    def get_group(self, uuid):
        url = "%s/groups/%s" % (self.url, uuid)
        r = requests.get(url)
        self.__raise_on_error(r)

        return r.json()

    def get_groups(self, page=None, limit=None, description=None, description_like=None, uuid=None):
        url = "%s/groups" % self.url
        r = requests.get(url, params=self.__prepare_params(_fparams()))
        self.__raise_on_error(r)

        return r.json()

    def create_result(self, outcome, testcase, groups=None, note=None, ref_url=None, **data):
        url = "%s/results" % self.url
        data = _fparams(expand_kwargs=False)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        self.__raise_on_error(r)

        return r.json()

    def get_result(self, id):
        url = "%s/results/%s" % (self.url, id)
        r = requests.get(url)
        self.__raise_on_error(r)

        return r.json()

    def get_results(self, page=None, limit=None, since=None, outcome=None, groups=None, testcases=None, testcases_like=None, raw_params=None, **kwargs):
        url = "%s/results" % self.url
        r = requests.get(url, params=self.__prepare_params(_fparams()))
        self.__raise_on_error(r)

        return r.json()

    def create_testcase(self, name, ref_url=None):
        url = "%s/testcases" % self.url
        data = _fparams()
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        self.__raise_on_error(r)

        return r.json()

    def update_testcase(self, name, url=_KEEP):
        data = {}
        if ref_url is not _KEEP:
            data['ref_url'] = ref_url
        if data:
            data['name'] = name

        url = "%s/testcases" % self.url
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        self.__raise_on_error(r)

        return r.json()

    def get_testcase(self, name):
        url = "%s/testcases/%s" % (self.url, name)
        r = requests.get(url)
        self.__raise_on_error(r)

        return r.json()

    def get_testcases(self, page=None, limit=None, name=None, name_like=None):
        url = "%s/testcases" % self.url
        r = requests.get(url, params=self.__prepare_params(_fparams()))
        self.__raise_on_error(r)

        return r.json()
