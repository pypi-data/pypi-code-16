import json

import logging

from . import settings
from .helpers import (SerenyticsException, make_request, HTTP_201_CREATED, HTTP_404_NOT_FOUND,
                      StorageJsonEncoder, StorageJsonDecoder, HTTP_429_TOO_MANY_REQUESTS)
from .settings import script_params
from .script import UnknownScript, Script
from .source import DataSource, UnknownDataSource
from .task import Task
from .user_preferences import UserPreferences
from .webapp import WebApp
from .version import __version__


logger = logging.getLogger(__name__)


def _init_headers(api_key):
    return {
        'X-Api-Key': api_key,
        'Content-type': 'application/json',
        'User-Agent': 'serenytics-python-client/%s' % __version__
    }


class Client(object):
    """
    Main wrapper around Serenytics API
    """

    def __init__(self, api_key=None, script_id=None):
        """
        :param api_key: [Optional] API key (get on https://app.serenytics.com/studio/account). Required if the script is
        run in local environment (e.g. on your computer) but it will be set automatically when run on Serenytics
        platform.
        :param script_id: [Optional] id of the script on Serenytics website, required if you plan on storing and
        retrieving data associated to the script between executions.
        """
        self._script_id = script_id
        api_key = api_key if api_key else script_params.get('SERENYTICS_API_KEY')
        self._headers = _init_headers(api_key)

        self._preferences = None

    def get_data_source_by_uuid(self, uuid):
        """
        Fetch a data source by uuid

        :param uuid: string
        :return: DataSource instance
        """
        data_source_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + uuid
        response = make_request('get', data_source_url,
                                custom_exceptions={HTTP_404_NOT_FOUND: UnknownDataSource(uuid)},
                                headers=self._headers)
        return DataSource(response.json(), client=self)

    def get_data_source_by_name(self, name):
        """
        Fetch a data source by its name.

        :param name: string
        :return: DataSource instance if there is exactly one data source with this name. Returns None if there isn't
        any data source with this name. Raise a SerenyticsException if there are multiple data sources with this name.
        """
        data_source_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source'
        params = {'q': json.dumps({'filters': [{'name': 'name', 'op': 'eq', 'val': name}]})}
        response = make_request('get', data_source_url,
                                params=params,
                                headers=self._headers)

        sources = response.json()

        if sources['num_results'] == 1:
            source = sources['objects'][0]
            return DataSource(source, client=self)

        elif sources['num_results'] > 1:
            raise SerenyticsException('There are multiple sources named "%s". Please rename other sources.' % name)

        return None

    def get_or_create_storage_data_source_by_name(self, name):
        """
        Retrieve the data source whose name is `name` or create a new one.

        :param name: string
        :return: DataSource instance
        """
        data_source = self.get_data_source_by_name(name)

        if data_source is not None:
            if data_source.type != 'Storage':
                raise SerenyticsException('Found a data source with this name "%s" but it is not a Storage data source'
                                          % name)
            return data_source

        data_source_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source'
        response = make_request('post', data_source_url,
                                data=json.dumps({'name': name, 'type': 'Storage', 'jsonContent': {}}),
                                expected_status_code=HTTP_201_CREATED,
                                headers=self._headers)
        source = response.json()
        return DataSource(source, client=self)

    def get_script_by_uuid(self, uuid):
        """
        Fetch a script by uuid

        :param uuid: string
        :return: Script instance
        """
        script_url = settings.SERENYTICS_API_DOMAIN + '/api/script/' + uuid
        response = make_request('get', script_url,
                                custom_exceptions={HTTP_404_NOT_FOUND: UnknownScript(uuid)},
                                headers=self._headers)
        return Script(response.json(), self._headers)

    def get_script_by_name(self, name):
        """
        Fetch a script by its name.

        :param name: string
        :return: Script instance if there is exactly one script with this name. Returns None if there isn't
        any script with this name. Raise a SerenyticsException if there are multiple scripts with this name.
        """
        script_url = settings.SERENYTICS_API_DOMAIN + '/api/script'
        params = {'q': json.dumps({'filters': [{'name': 'name', 'op': 'eq', 'val': name}]})}
        response = make_request('get', script_url,
                                params=params,
                                headers=self._headers)

        scripts = response.json()

        if scripts['num_results'] == 1:
            script = scripts['objects'][0]
            return Script(script, self._headers)

        elif scripts['num_results'] > 1:
            raise SerenyticsException('There are multiple scripts named "%s". Please rename other scripts.' % name)

        return None

    @property
    def _script_storage_url(self):
        if self._script_id is None:
            raise SerenyticsException('You must initialize the client with the script_id before using script storage')
        return settings.SERENYTICS_API_DOMAIN + '/api/script/' + self._script_id + '/storage'

    def store_script_data(self, data):
        """
        Store script data to be retrieved during next execution of the script.

        :param data: any data that can be serialized to json
        """
        make_request('put', self._script_storage_url,
                     data=json.dumps(data, cls=StorageJsonEncoder),
                     headers=self._headers)

    def retrieve_script_data(self):
        """
        Retrieve script data saved in previous script execution.
        """
        response = make_request('get', self._script_storage_url, headers=self._headers)
        try:
            return json.loads(response._content.decode('utf-8'), cls=StorageJsonDecoder)
        except Exception as e:
            logger.warning('Failed to decode storage data: %s' % e)
            return None

    @property
    def script_args(self):
        """
        Get args passed to the script

        Obsolete: will be removed in next version
        """
        return script_params

    def send_email(self, subject, recipients, html, web_app_uuid=None, pdf_file_name=None):
        """
        Send an email through Serenytics API

        :param subject: String containing the email subject
        :param recipients: List of strings containing recipients email addresses
        :param html: String containing HTML body
        :param web_app_uuid: (Optional) String uuid of webapp to include as a PDF attachment in the email
        :param pdf_file_name: (Optional) Name of webapp pdf file attached to the email (default: WEBAPP_NAME.pdf)
        """
        response = make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/email',
                                headers=self._headers,
                                custom_exceptions={HTTP_429_TOO_MANY_REQUESTS: TooManyEmailsSent()},
                                data=json.dumps({
                                    'subject': subject,
                                    'recipients': recipients,
                                    'html': html,
                                    'web_app_uuid': web_app_uuid,
                                    'pdf_file_name': pdf_file_name
                                }))
        task = Task(task_id=response.json()['task_id'], description='Send email', headers=self._headers)
        task.wait()
        task.raise_on_error()

    def refresh_cache_for_web_app(self, web_app_uuid):
        """
        Warm up Serenytics data cache for given dashboard (web_app_uuid).

        :param web_app_uuid: (Optional) String uuid of webapp to refresh cache for
        """
        make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/web_app/' + web_app_uuid + '/generate_pdf',
                     headers=self._headers,
                     data=json.dumps({
                         'store_pdf': False,
                     }))

    def get_webapps(self):
        """
        Return all webapps (dashboards) of authenticated user

        :return: WebApp list
        """
        webapps_url = settings.SERENYTICS_API_DOMAIN + '/api/web_app'
        response = make_request('get', webapps_url,
                                headers=self._headers)
        return [WebApp(config, client=self) for config in response.json()['objects']]

    @property
    def preferences(self):
        """
        Return preferences of authenticated user
        """
        if self._preferences is None:
            response = make_request('get', settings.SERENYTICS_API_DOMAIN + '/api/me/preferences',
                                    headers=self._headers)
            self._preferences = UserPreferences(response.json())
        return self._preferences


class TooManyEmailsSent(SerenyticsException):
    """Exception raised when more emails are sent than authorized by the current rate limit"""
