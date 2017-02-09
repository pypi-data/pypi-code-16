#
# Copyright 2016 Import.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CREDENTIALS_FILE_NAME = 'sheets.googleapis.com-python-quickstart.json'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args([])
except ImportError:
    flags = None


class GoogleSheet(object):

    def __init__(self):
        self._service = None
        self._range = range

    def authorize(self, application_name, client_secret_path):
        credential_path = self.credential_path()
        store = oauth2client.file.Storage(credential_path)
        flow = client.flow_from_clientsecrets(client_secret_path, SCOPES)
        flow.user_agent = application_name
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)

    def credential_path(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, CREDENTIALS_FILE_NAME)
        return credential_path

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        credential_path = self.credential_path()
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        return credentials

    def initialize_service(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        self._service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)

    def get_urls(self, spreadsheet_id, sheet_range):
        result = self._service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                           range=sheet_range).execute()
        values = result.get('values', [])
        urls = []
        for v in values:
            urls.append(v[0])
        return urls

