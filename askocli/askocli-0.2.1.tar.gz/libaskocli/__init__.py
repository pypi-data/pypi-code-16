"""Contain functions to manage script arguments
and RequestApi class to communicate with the distant
AskOmics server"""

import os
from os.path import basename
import json
import requests
# import logging

# logging.getLogger('requests').setLevel(logging.CRITICAL)
# log = loggin.getLoger()

def askomics_auth(parser):
    """manage authentication arguments

    :param parser: the parser
    :type parser: argparse
    """

    parser.add_argument('-u', '--username', help='You AskOmics username', required=True)
    parser.add_argument('-k', '--apikey', help='An API key associate with your account', required=True)

def askomics_url(parser):
    """manage askomics arguments

    :param parser: the parser
    :type parser: argparse
    """

    parser.add_argument('-a', '--askomics', help='AskOmics URL', required=True)
    parser.add_argument('-p', '--port', help='AskOmics port')


class RequestApi(object):
    """RequestApi contain method to communicate with
    the AskOmics API"""


    def __init__(self, url, username, apikey, file_type):

        self.url = url
        self.cookies = None
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.username = username
        self.apikey = apikey
        self.col_types = None
        self.key_columns = [0] # Default value
        self.path = None
        self.type = file_type

    def set_cookie(self):
        """set the session cookie of user

        :returns: session cookie of username
        :rtype: cookies
        """


        json_dict = {
            'username': self.username,
            'apikey': self.apikey
        }

        url = self.url + '/login_api'

        try:
            response = requests.post(url, json=json_dict)
        except Exception as exc:
            print('Error: ' + str(exc))

        # print(response.text)

        # Check the passwd
        if 'error' in json.loads(response.text):
            if json.loads(response.text)['error']:
                print('Error:\n' + '\n'.join(json.loads(response.text)['error']))

        cookies = response.cookies

        self.cookies = cookies

    def upload_file(self):
        """Upload a file into tmp dir of user

        :returns: the response dict
        :rtype: dict
        """

        url = self.url + '/up/file'
        files = {
            basename(self.path): open(self.path, 'rb')
        }

        response = requests.post(url, files=files, cookies=self.cookies, headers=self.headers)

        if 'error' in json.loads(response.text):
            print('Error:\n' + json.loads(response.text)['error'])

        return response.text

    def set_key_columns(self, keycols):
        """Set the key columns

        :param keycols: list of key index
        :type keycols: list
        """

        self.key_columns = keycols

    def set_filepath(self, path):
        """set the file path"""

        self.path = path

    def guess_col_types(self):
        """Guess the colomns type of a csv file"""

        url = self.url + '/guess_csv_header_type'

        json_dict = {
            'filename': basename(self.path)
        }

        response = requests.post(url, cookies=self.cookies, headers=self.headers, json=json_dict)

        if 'error' in json.loads(response.text):
            print('Error:\n' + json.loads(response.text)['error'])


        self.col_types = json.loads(response.text)['types']
        self.col_types[0] = 'entity_start'


    def integrate_data(self):
        """Integrate the csv file into the triplestore

        :returns: response text
        :rtype: string
        """


        url = self.url + '/load_data_into_graph'


        json_dict = {
            'file_name': basename(self.path),
            'col_types': self.col_types,
            'disabled_columns': [],
            'key_columns': self.key_columns,
            'public': False,
            'forced_type': self.type
        }

        response = requests.post(url, cookies=self.cookies, headers=self.headers, json=json_dict)

        if 'error' in json.loads(response.text):
            print('Error:\n' + json.loads(response.text)['error'])

        return response.text

    def integrate_gff(self, taxon, entities):
        """Integrate a gff into the triplestore

        :param taxon: taxon
        :type taxon: string
        :param entities: list of entities to integrate
        :type entities: list
        :returns: response text
        :rtype: string
        """

        url = self.url + '/load_gff_into_graph'

        json_dict = {
            'file_name': basename(self.path),
            'taxon': taxon,
            'entities': entities,
            'public': False,
            'forced_type': self.type
        }

        response = requests.post(url, cookies=self.cookies, headers=self.headers, json=json_dict)

        if 'error' in json.loads(response.text):
            print('ERROR: ' + json.loads(response.text)['error'])

        return response.text

    def integrate_ttl(self):
        """Integrate a ttl into the triplestore

        :returns: response text
        :rtype: string
        """

        url = self.url + '/load_ttl_into_graph'

        json_dict = {
            'file_name': basename(self.path),
            'public': False,
            'forced_type': self.type
        }

        response = requests.post(url, cookies=self.cookies, headers=self.headers, json=json_dict)

        if 'error' in json.loads(response.text):
            print('ERROR: ' + json.loads(response.text)['error'])

        return response.text
