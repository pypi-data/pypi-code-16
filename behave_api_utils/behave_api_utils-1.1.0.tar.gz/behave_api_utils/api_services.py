import json
from abc import ABCMeta

from behave_api_utils import RESTOperation, send_request, add_url_query_parameters
from behave_logger import get_logger

logger = get_logger(__name__)


def get_api_auth_headers(credentials):
    """
    Creates authorization headers for api auth

    :param credentials:
        User, key dict representing for creating api auth headers
    :return:
        dict with the headers required for api-auth
    """
    try:
        return {
            'ApiAuth-ApiUser': credentials["user"],
            'ApiAuth-ApiKey': credentials["key"]
        }
    except IndexError:
        raise ValueError("credentials should be an user, key dict")


class APIRequestBase(object):
    """
     Abstract class modeling the basic operation of a REST service.
     """
    __metaclass__ = ABCMeta

    def __init__(self, api_url_path, base_url):
        """
        Initializes the class

        :param api_url_path:
            Relative path where the API is going to run
        :param base_url:
            URL of the service or proxy to test
        """
        self._base_url = base_url
        self.api_url = '/'.join((self._base_url, api_url_path))
        self.query_params = {}
        self._response = None
        self.response_json_dict = {}

    @property
    def response_content_length(self):
        length = self.response.headers['Content-Length']
        logger.info('Response Content-Length: {} chars'.format(length))
        return length

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, received_response):
        """
        Stores the received response and tries to convert it to JSON dict

        :param received_response:
            String representing a response
        """
        self._response = received_response
        try:
            self.response_json_dict = json.loads(received_response.text)
        except (ValueError, AttributeError):
            self.response_json_dict = {}

    def add_query_parameter(self, key, value):
        """
        Sets a query parameter to be used on get_output method.

        :param key:
            String representing parameter name
        :param value:
            String representing value data
        """
        if isinstance(value, unicode):
            value = value.encode("utf-8")

        self.query_params[key] = value

    def clear_query_parameters(self):
        """
        Clears the query parameters
        :return:
        """
        self.query_params = {}

    def get_json(self, endpoint_resource, custom_path=None, operation=RESTOperation.GET,
                 headers=None):
        """
        Gets an endpoint resource output.

        :param endpoint_resource:
            A String representing the endpoint resource to get
        :param custom_path:
            A String representing an additional path to include
        in the request's URI
        :param operation:
            (Optional) A 'RESTOperation' Enum specifying the REST Operation to execute
            in the endpoint. GET is the default option
        :param headers:
            (Optional) A dict object to specify additional headers
        :return:
            A JSON representing the endpoint resource's output
        """
        url = '/'.join((self.api_url, endpoint_resource))

        if custom_path is not None:
            url = '/'.join((url, custom_path))

        if len(self.query_params) > 0:
            url = add_url_query_parameters(url, self.query_params)

        self.response = send_request(operation, url, headers)
        self.clear_query_parameters()

        return self.response_json_dict


class ServicesAPIBase(APIRequestBase):
    """
    Abstract class modeling common operations on services testing
    """
    __metaclass__ = ABCMeta

    def __init__(self, api_url_path, base_url=None, requires_data_validation=False,
                 credentials=None, proxy=None):
        """
        Initializes the class according to the URL to run the service, API auth credentials and
        the proxy to run through

        :param api_url_path:
            Relative path where the API is going to run
        :param base_url:
            URL of the service or proxy to test
        :param requires_data_validation:
            True if data validation is required, False otherwise
        :param credentials:
            User, key dictionary representing credentials to be used or None if no credentials
            are required
        :param proxy: A ProxyBase class child's instance

        """
        self._proxy = proxy
        self._requires_data_validation = requires_data_validation

        # Set base url according to proxy
        if proxy:
            assert not base_url, "When running through a proxy, base_url parameter is not used."
            base_url = proxy.proxy_url
        else:
            assert base_url, "Base URL is required when running directly against service"

        # Set auth headers
        if isinstance(proxy, ApigeeProxy):
            assert not credentials, "When running through apigee, API credentials are not used"
            proxy.log_in()
            self._auth_headers = proxy.auth_header
        else:
            if credentials:
                self._auth_headers = get_api_auth_headers(credentials)
            else:
                self._auth_headers = {}

        super(ServicesAPIBase, self).__init__(api_url_path, base_url)

    def get_authorization_headers(self, user_credentials='given on init'):
        """
        Creates authorization headers based on the specified proxy and received credentials

        :param user_credentials:
            'given on init' String for using credentials set on init, a {user, key} dict
            with the credentials to be used or None to discard api auth headers.
        :return:
            dict with the headers according to specified credentials and object's proxy property
        """
        if isinstance(self._proxy, ApigeeProxy):
            assert not user_credentials, \
                "When running through Apigee, API credentials are not used"
            headers = self._auth_headers
        else:
            if user_credentials == 'given on init':
                headers = self._auth_headers
            elif isinstance(user_credentials, dict):
                headers = get_api_auth_headers(user_credentials)
            elif not user_credentials:
                headers = {}
            else:
                raise ValueError("Invalid data '{}' for user_credentials: "
                                 "Allowed values, 'given on init', dict with user and key"
                                 " or None".format(user_credentials))

        return headers

    def add_query_parameter(self, key, value):
        """
        Sets a query parameter to be used on get_output method.

        :param key:
            String representing parameter name
        :param value:
            String representing value data
        """
        if isinstance(value, unicode):
            value = value.encode("utf-8")

        self.query_params[key] = value

    def clear_query_parameters(self):
        """
        Clears the query parameters
        :return:
        """
        self.query_params = {}

    @staticmethod
    def _merge_headers(header_dict1, header_dict2):
        if not header_dict1:
            header_dict1 = {}
        if not header_dict2:
            header_dict2 = {}

        final_headers = header_dict1
        final_headers.update(header_dict2)

        return final_headers

    def validate_data_structure(self, operation, endpoint_resource, data):
        """
        Validates the data to be used in endpoint operations. It must be implemented in child
        classes when it is required to model validation according to specific data structure
        in each service

        :param operation:
            String representing a endpoint operation. Allowed values: "create", "update"
        :param endpoint_resource:
            String representing the endpoint to validate_data_structure. It can be used to
            determine different validations according to the endpoint.
        :param data:
            Data dictionary to check.
        :return:
            True if data is valid, False otherwise
        """
        raise NotImplementedError()

    def get_auth_output(self, endpoint_resource, custom_path=None, user_credentials=None,
                        operation=RESTOperation.GET, headers=None):
        """
        Gets an endpoint resource output. If no credentials are specified,
        the ones given on instance init will be used

        :param endpoint_resource:
            A String representing the endpoint resource to get
        :param custom_path:
            A String representing an additional path to include
        in the request's URI
        :param user_credentials:
            (Optional) A JSON representing the credentials as {'user':'user_name',
            'key': 'user_key'}, 'given on init' String to use the ones set on init or
            None to discard authorization credentials
        :param operation:
            (Optional) A 'RESTOperation' Enum specifying the REST Operation to execute
            in the endpoint. GET is the default option
        :param headers:
            (Optional) A dict object to specify additional headers
        :return:
            A JSON representing the endpoint resource's output
        """
        final_headers = self._merge_headers(self.get_authorization_headers(user_credentials),
                                            headers)

        self.get_json(endpoint_resource, custom_path, operation, final_headers)
        self.clear_query_parameters()

        return self.response_json_dict

    def create(self, endpoint_resource, user_credentials='given on init', headers=None, **kwargs):
        """
        Creates a record in the specified endpoint by using data specified in kwargs

        :param endpoint_resource:
            String representing the endpoint where the record is going to be created
        :param user_credentials:
            (Optional) A JSON representing the credentials as {'user':'user_name',
            'key': 'user_key'}, 'given on init' String to use the ones set on init or
            None to discard authorization credentials
        :param headers:
            (Optional) A dict object to specify additional headers
        :param kwargs:
            Data to use on record creation.
        :return:
            Id of the created record \n
        """
        if self._requires_data_validation:
            assert self.validate_data_structure("create", endpoint_resource, kwargs), \
                "Data validation failed on record creation. Check logs for more information."

        url = '/'.join((self.api_url, endpoint_resource, ""))

        final_headers = self.get_authorization_headers(user_credentials)
        final_headers["Content-Type"] = "application/json"

        merged_headers = self._merge_headers(final_headers, headers)

        logger.info("Creating '{}' '[{}]'".format(endpoint_resource, kwargs))
        self.response = send_request(RESTOperation.POST, url, merged_headers, kwargs)

        try:
            return self.response_json_dict["id"]
        except KeyError:
            return None

    def delete(self, endpoint_resource, resource_key, user_credentials='given on init',
               headers=None):
        """
        Deletes a record of an endpoint by using its key

        :param endpoint_resource:
            String representing the endpoint where the record is going to be deleted
        :param resource_key:
            String representing the key of the record to be deleted
        :param user_credentials:
            (Optional) A JSON representing the credentials as {'user':'user_name',
            'key': 'user_key'}, 'given on init' String to use the ones set on init or
            None to discard authorization credentials
        :param headers:
            (Optional) A dict object to specify additional headers
        """
        endpoint_url = '/'.join((self.api_url, endpoint_resource, resource_key, ""))
        final_headers = self._merge_headers(self.get_authorization_headers(user_credentials),
                                            headers)

        logger.info("Deleting resource '{}' - Id: '{}'".format(endpoint_resource, resource_key))
        self.response = send_request(RESTOperation.DELETE, endpoint_url, final_headers)

    def update(self, endpoint_resource, resource_key, operation=RESTOperation.PATCH,
               user_credentials='given on init', headers=None, **kwargs):
        """
        Updates a record for an endpoint by using its key

        :param endpoint_resource:
            String representing the endpoint where the record is going to be updated
        :param resource_key:
            String representing the key of the record to update
        :param operation:
            (Optional) RESTOperation enum value representing the operation to perform in the API.
            Default Value: PATCH
        :param user_credentials:
            (Optional) A JSON representing the credentials as {'user':'user_name',
            'key': 'user_key'}, 'given on init' String to use the ones set on init or
            None to discard authorization credentials
        :param headers:
            (Optional) A dict object to specify additional headers
        :param kwargs:
            Data to use on record update.
        """
        allowed_ops = (RESTOperation.PATCH, RESTOperation.PUT)
        assert operation in allowed_ops, "Operation '{}' is not allowed for update. " \
                                         "Allowed operations '{}'".format(operation, allowed_ops)

        if self._requires_data_validation:
            assert self.validate_data_structure("update", endpoint_resource, kwargs), \
                "Data validation failed on record updating. Check logs for more information."

        endpoint_url = '/'.join((self.api_url, endpoint_resource, resource_key, ""))
        final_headers = self.get_authorization_headers(user_credentials)
        final_headers["Content-Type"] = "application/json"

        merged_headers = self._merge_headers(final_headers, headers)

        logger.info("Updating resource '{}' - Id: '{}'".format(endpoint_resource,
                                                               resource_key))
        self.response = send_request(operation, endpoint_url, merged_headers, kwargs)


class ProxyBase(object):
    """
    Base class for modeling proxy services that can be used for services to run through
    """
    __metaclass__ = ABCMeta

    def __init__(self, proxy_url, proxy_id=None, key=None):
        """
        Initializes the class

        :param proxy_url: String representing proxy's URL
        :param proxy_id: String to be used as identifier for authentication when needed
        :param key: String to be used as key for authentication when needed
        """
        self.proxy_url = proxy_url
        self._id = proxy_id
        self._key = key


class ApigeeProxy(ProxyBase, APIRequestBase):
    def __init__(self, proxy_url, client_id, client_secret):
        """
        Initializes the class

        :param proxy_url: String representing proxy's URL
        :param client_id: String representing Apigee client Id
        :param client_secret:  String representing client secret
        """
        ProxyBase.__init__(self, proxy_url, client_id, client_secret)
        APIRequestBase.__init__(self, "", self.proxy_url)

    @property
    def access_token(self):
        return self.response_json_dict['access_token']

    @property
    def auth_header(self):
        return {"Authorization": "Bearer {}".format(self.access_token)}

    def log_in(self):
        """
        Logs into Apigee \n
        :return: Returns the response of the login to Apigee with valid credentials. \n
        """
        url = "/".join((self._base_url, "oauth/accesstoken"))
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = "grant_type=client_credentials&client_id={}" \
                  "&client_secret={}".format(self._id, self._key)

        self.response = send_request(RESTOperation.POST, url, headers, payload)


class RelayProxy(ProxyBase):
    pass
