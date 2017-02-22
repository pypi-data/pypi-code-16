
import logging_helper
from _metadata import __version__, __authorshort__
from resources import templates, schema
from configurationutil import Configuration, cfg_params

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = u'networkutils'
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
ENDPOINT_LOOKUP_CONFIG = u'endpoint_lookup'
ENDPOINTS_CONFIG = u'{c}.endpoints'.format(c=ENDPOINT_LOOKUP_CONFIG)
ENVIRONMENTS_CONFIG = u'{c}.environments'.format(c=ENDPOINT_LOOKUP_CONFIG)
TEMPLATE = templates.endpoints

# Constants for accessing config items
ACTIVE = u'active'
DESCRIPTION = u'DESCRIPTION'


# OLD
HOSTNAME = u'hostname'
PORT = u'port'
ENDPOINT = u'endpoint'
API_SIGNATURE = u'api_signature'
API_SIGNATURES = u'api_signatures'
API = u'api'
ENVIRONMENT = u'environment'
PARAMETERS = u'parameters'


def __register_endpoints_lookup_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=ENDPOINT_LOOKUP_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.endpoints)

    return cfg


def get_endpoints():

    # Register configuration
    cfg = __register_endpoints_lookup_config()

    endpoints = cfg[ENDPOINTS_CONFIG]
    logging.debug(endpoints)

    # Return a copy so that modifications of the retrieved do not get modified in config unless explicitly requested!
    return endpoints.copy()


def get_environments():

    # Register configuration
    cfg = __register_endpoints_lookup_config()

    environments = cfg[ENVIRONMENTS_CONFIG]
    logging.debug(environments)

    # Return a copy so that modifications of the retrieved do not get modified in config unless explicitly requested!
    return environments.copy()


class Endpoint(object):

    def __init__(self,
                 hostname,
                 port,
                 api_signatures,
                 api,
                 environment,
                 parameters):

        self.hostname = hostname
        self.port = port
        self.__extract_api_signatures(api_signatures)
        self.api = api
        self.environment = environment
        self.__extract_parameters(parameters)

    def __extract_api_signatures(self,
                                 api_signatures):

        """
        Turns a comma separated list of key value pairs into instance attributes
        :param api_signatures:
        :return:
        """

        try:
            self.api_signatures = [api_signature.strip() for api_signature in api_signatures.split(u',')]

        except AttributeError:
            self.api_signatures = []

    def __extract_parameters(self,
                             parameters):

        """
        Turns a comma separated list of key value pairs into instance attributes
        :param parameters:
        :return:
        """

        try:
            parameters = parameters.split(u',') if parameters.strip() else []

        except AttributeError:
            self.parameters = None
            return

        try:
            key_value_pairs = [parameter.split(u':') for parameter in parameters]

            for key, value in key_value_pairs:
                setattr(self, key.strip(), value.strip())

        except ValueError:
            self.parameters = None

    def __getitem__(self,
                    item):
        return self.__getattribute__(item)

    def url_match_length(self,
                         url):

        url_match_length = - 1

        if u'://' in url:
            protocol, url = url.split(u'://')

        hostname = url.split(u'/')[0]

        if u':' in hostname:
            hostname, port = hostname.split(u':')

            if port != self.port:
                return url_match_length

        if hostname != self.hostname:
            return url_match_length

        url_match_length = 0  # Match for hostname

        call = u'/'.join(url.split(u'/')[1:])

        for api_signature in self.api_signatures:
            if len(api_signature) > url_match_length and call.startswith(api_signature):
                url_match_length = len(api_signature)

        return url_match_length


class Endpoints(object):

    def __init__(self):
        self._endpoints = get_endpoints()

    @property
    def endpoints(self):
        return self._endpoints

    @staticmethod
    def __single_endpoint(endpoints,
                          conditions):

        """
        checks for endpoints list having just one item and returns it in that
        case or raises an exception otherwise

        :param endpoints: [Endpoint,...Endpoint].
        :param conditions: string indicating the list of conditions used
                           in the lookup. This is just for logging exceptions.
        :return: Endpoint
        """

        if isinstance(endpoints, Endpoint):
            return endpoints

        if len(endpoints) == 0:
            raise LookupError(u'No matching endpoints for {conditions}'.format(conditions=conditions))

        elif len(endpoints) > 1:
            raise LookupError(u'Multiple matching endpoints for {conditions}'.format(conditions=conditions))

        return endpoints[0]

    def get_endpoint(self,
                     api,
                     environment,
                     ):

        logging.debug(api)
        logging.debug(environment)

        conditions = (u'api={api}; environment={environment}'.format(api=api,
                                                                     environment=environment))

        matching_endpoints = [endpoint for endpoint in self.endpoints
                              if endpoint.api == api and endpoint.environment == environment]

        return self.__single_endpoint(endpoints=matching_endpoints,
                                      conditions=conditions)

    def get_endpoint_for_request(self,
                                 url):

        logging.debug(url)
        best_match = - 1
        matched_endpoints = []

        for endpoint in self.endpoints:
            matched_len = endpoint.url_match_length(url)

            if matched_len > -1:
                if matched_len > best_match:
                    matched_endpoints = [endpoint]

                elif matched_len == best_match:
                    matched_endpoints.append(endpoint)

        if len(matched_endpoints) == 1:
            return matched_endpoints[-1]

        if len(matched_endpoints) == 0:
            raise LookupError(u'No endpoint match for: {url}'.format(url=url))

        raise LookupError(u'Multiple matching endpoints for: {url}\n(Check you endpoint config)'.format(url=url))

    def get_apis_for_host(self,
                          hostname):
        return [endpoint.api for endpoint in self.endpoints if hostname == endpoint.hostname]

    # Not Currently used!
    def get_endpoints_for_host(self,
                               hostname):
        return [endpoint for endpoint in self.endpoints if hostname == endpoint.hostname]

    # Not Currently used!
    def get_endpoint_for_host(self,
                              hostname):
        return [endpoint.api for endpoint in self.endpoints if hostname == endpoint.hostname][0]

    def get_environments_for_api(self,
                                 api):
        return [endpoint.environment for endpoint in self.endpoints if api == endpoint.api]

    def get_environment_for_host(self,
                                 hostname):
        matched_environments = set([endpoint.environment for endpoint in self.endpoints
                                    if endpoint.hostname == hostname])

        if len(matched_environments) != 1:
            raise LookupError(u'Ambiguous environments for {hostname}'.format(hostname=hostname))

        return matched_environments.pop()

    def get_endpoint_apis(self):
        return {endpoint.hostname: endpoint.api for endpoint in self.endpoints}

    # Only used by below
    def get_endpoint_for_api_and_environment(self,
                                             api,
                                             environment):
        return [endpoint for endpoint in self.endpoints if endpoint.api == api and endpoint.environment == environment]

    # Used once to get the hostname (not sure why when hostname is used to get apis!)
    def get_endpoints_for_apis_and_environment(self,
                                               apis,
                                               environment):
        return [self.get_endpoint_for_api_and_environment(api=api, environment=environment) for api in apis]

if u'endpoints' not in locals():
    endpoints = Endpoints()


if __name__ == u'__main__':

    endpoint_dict = {HOSTNAME: u'hostname',
                     PORT: u'8080',
                     API_SIGNATURES: u'api_signature/',
                     API: u'api',
                     ENVIRONMENT: u'environment',
                     PARAMETERS: u'k1:v1, k2:v2', }

    ep = Endpoint(**endpoint_dict)

    print ep
