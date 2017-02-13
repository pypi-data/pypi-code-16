import sys
import ssl
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
from colors import ANSIColors


logger = logging.getLogger(__name__)
TILDA = f'{ANSIColors.BLUE}~{ANSIColors.ENDC}'


class APIClient:
    """
    GitLab simplified API client.
    """
    AUTH_FAILED = f'{TILDA} {ANSIColors.RED}Authentication failure.{ANSIColors.ENDC} Probably your token is wrong.'

    def __init__(self, base_url, project_id, token, **kwargs):
        self.base_url = base_url
        self.project_id = project_id
        self.token = token

        self.debug = kwargs.get('debug', False)
        cert_path = kwargs.get('cert_path', None)
        if cert_path is not None:
            self.ssl_context = ssl.create_default_context(cafile=cert_path)

    def get_request(self, url):
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'PRIVATE-TOKEN': self.token,
                'Content-Type': 'application/json'
            }
        )
        return req

    def make_request(self, request):
        try:
            if hasattr(self, 'ssl_context'):
                response = urllib.request.urlopen(request, context=self.ssl_context)
            else:
                response = urllib.request.urlopen(request)
            return response
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(self.AUTH_FAILED)
            elif e.code == 400:
                raise e
            sys.exit(1)

    def fetch(self):
        endpoint = f'{self.base_url}/projects/{self.project_id}/variables'
        if self.debug:
            logger.debug('Making GET request {0}'.format(endpoint))
        request = self.get_request(endpoint)
        response = self.make_request(request)
        payload = json.loads(response.read().decode('utf-8'))
        if len(payload) == 0:
            print(f'{TILDA} No variables.')
        else:
            for variable in payload:
                print(f'{ANSIColors.GREEN}{variable["key"]}{ANSIColors.ENDC}: {variable["value"]}')

    def projects(self):
        endpoint = f'{self.base_url}/projects?simple=true'
        request = self.get_request(endpoint)
        response = self.make_request(request)
        payload = json.loads(response.read().decode('utf-8'))
        for project in payload:
            print(f'{ANSIColors.GREEN}{project["name"]}{ANSIColors.ENDC} - {project["id"]}')

    def set(self, variables):
        print(f'{TILDA} Setting {ANSIColors.GREEN}{", ".join(variables.keys())}{ANSIColors.ENDC}...')
        for key, value in variables.items():
            print(key, value)
            endpoint = f'{self.base_url}/projects/{self.project_id}/variables'
            request = self.get_request(endpoint)
            request.get_method = lambda: 'POST'
            request.data = json.dumps({'key': key, 'value': value}).encode('utf-8')
            try:
                logger.debug('Making POST request {0}'.format(endpoint))
                if hasattr(self, 'ssl_context'):
                    response = urllib.request.urlopen(request, context=self.ssl_context)
                else:
                    response = urllib.request.urlopen(request)
                payload = json.loads(response.read().decode('utf-8'))
                print(f'{ANSIColors.GREEN}{key}{ANSIColors.ENDC}: {value}')
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    print(f'~ Variable {ANSIColors.RED}{key}{ANSIColors.ENDC} is already set.')
                elif e.code == 401:
                    print(self.AUTH_FAILED)
                else:
                    raise e

    def unset(self, variables):
        for variable in variables:
            print(f'{TILDA} Unsetting {ANSIColors.GREEN}{variable}{ANSIColors.ENDC}...')
            endpoint = f'{self.base_url}/projects/{self.project_id}/variables/{variable}'
            request = self.get_request(endpoint)
            request.get_method = lambda: 'DELETE'

            try:
                logger.debug('Making DELETE request {0}'.format(endpoint))
                if hasattr(self, 'ssl_context'):
                    response = urllib.request.urlopen(request, context=self.ssl_context)
                else:
                    response = urllib.request.urlopen(request)
                payload = json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f'~ Variable {ANSIColors.RED}{variable}{ANSIColors.ENDC} not found.')
                elif e.code == 401:
                    print(self.AUTH_FAILED)

    def clear(self):
        print(f'{TILDA} Resetting all secret variables.')
        endpoint = f'{self.base_url}/projects/{self.project_id}/variables'
        request = self.get_request(endpoint)
        response = self.make_request(request)
        payload = json.loads(response.read().decode('utf-8'))
        for variable in payload:
            key = variable['key']
            print(f'~ Unsetting {ANSIColors.GREEN}{key}{ANSIColors.ENDC}...')
            endpoint = f'{self.base_url}/projects/{self.project_id}/variables/{key}'
            request = self.get_request(endpoint)
            request.get_method = lambda: 'DELETE'

            try:
                response = urllib.request.urlopen(request, context=self.ssl_context)
                payload = json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f'~ Variable {ANSIColors.RED}{key}{ANSIColors.ENDC} not found.')
                elif e.code == 401:
                    print(self.AUTH_FAILED)
