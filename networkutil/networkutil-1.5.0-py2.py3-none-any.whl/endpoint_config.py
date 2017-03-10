
import logging_helper
from _metadata import __version__, __authorshort__, __module_name__
from resources import templates, schema
from configurationutil import Configuration, cfg_params

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
ENDPOINT_LOOKUP_CONFIG = u'endpoint_lookup'

ENDPOINTS_CONFIG = u'{c}.endpoints'.format(c=ENDPOINT_LOOKUP_CONFIG)
ENVIRONMENTS_CONFIG = u'{c}.environments'.format(c=ENDPOINT_LOOKUP_CONFIG)
APIS_CONFIG = u'{c}.apis'.format(c=ENDPOINT_LOOKUP_CONFIG)

TEMPLATE = templates.endpoints

# Endpoint property keys
_EP_PORT = u'port'
_EP_ENV = u'environment'
_EP_APIS = u'apis'


def _register_endpoints_lookup_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=ENDPOINT_LOOKUP_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.endpoints)

    return cfg


class EnvAndAPIs(object):

    # API PROPERTY KEYS
    API_KEY = u'key'
    API_SECRET = u'secret'
    API_USER = u'user'
    API_PASSWORD = u'password'
    API_METHODS = u'methods'
    API_PARAMETERS = u'parameters'

    def __init__(self):
        self._cfg = _register_endpoints_lookup_config()

    def get_apis(self):

        apis = self._cfg[APIS_CONFIG]
        logging.debug(apis)

        # Return a copy so that the retrieved does not get modified in config unless explicitly requested!
        return apis.copy()

    def get_api_list(self):
        return self.get_apis().keys()

    def get_environments(self):

        environments = self._cfg[ENVIRONMENTS_CONFIG]
        logging.debug(environments)

        # Return a copy so that the retrieved does not get modified in config unless explicitly requested!
        return environments

    def get_apis_for_environment(self,
                                 env):

        return self._cfg.find(APIS_CONFIG, [(env, None)]).keys()

    def get_environments_for_api(self,
                                 api):

        apis = self.get_apis()
        api = apis.get(api)

        return api.keys()


class Endpoint(object):

    # Endpoint property keys
    EP_PORT = _EP_PORT
    EP_ENV = _EP_ENV
    EP_APIS = _EP_APIS

    def __init__(self,
                 hostname,
                 port,
                 environment,
                 apis,
                 methods=None,
                 parameters=None):

        self.hostname = hostname
        self.port = port
        self.apis = apis
        self.environment = environment
        self.methods = methods if methods is not None else {}
        self.parameters = self.__extract_parameters(parameters)

    def endpoint(self,
                 method_name=None,
                 default_method=u''):

        method = self.method(method_name=method_name,
                             default_method=default_method)

        endpoint = u'{host}:{port}{method_sep}{method}'.format(host=self.hostname,
                                                               port=self.port,
                                                               method_sep=u'/' if not method.startswith(u'/') else u'',
                                                               method=method)

        return endpoint

    def method(self,
               method_name,
               default_method=u''):
        return self.methods.get(method_name, default_method)

    def __extract_parameters(self,
                             parameters):

        """
        Turns a comma separated list of key value pairs into instance attributes

        :param parameters:

        :return:
        """

        if parameters is None:
            parameters = {}

        for key, value in parameters.iteritems():
            setattr(self, key, value)

        return parameters

    def __getitem__(self,
                    item):
        return self.__getattribute__(item)

    def url_match_length(self,
                         url):

        url_match_length = -1

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

        for api_signature in self.methods.values():
            if (len(api_signature) > url_match_length and
                    call.startswith(api_signature)):
                url_match_length = len(api_signature)

        return url_match_length

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        string = (u'Hostname:{hostname}:{port}\n'
                  u'API:{api}\n'
                  u'Environment:{env}'.format(hostname=self.hostname,
                                              port=self.port,
                                              api=self.apis,
                                              env=self.environment))

        if self.methods:
            methods = [u'{key}:{value}'.format(key=key,
                                               value=value)
                       for key, value in self.methods.iteritems()]

            string += u'\nMethods:{methods}\n'.format(methods=u'\n        '.join(methods))

        for key, value in self.parameters.iteritems():
            string += u'{key}:{value}\n'.format(key=key,
                                                value=value)

        return string


class Endpoints(object):

    # Endpoint property keys
    EP_PORT = _EP_PORT
    EP_ENV = _EP_ENV
    EP_APIS = _EP_APIS

    def __init__(self):
        self._cfg = _register_endpoints_lookup_config()
        self._endpoints = {ep_name: Endpoint(hostname=ep_name, **ep) for ep_name, ep in self.raw_endpoints.iteritems()}

    @property
    def raw_endpoints(self):

        endpoints = self._cfg[ENDPOINTS_CONFIG]
        logging.debug(endpoints)

        # Return a copy so that modifications of the retrieved do not get modified in config unless explicitly requested!
        return endpoints.copy()

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
                     environment):

        logging.debug(api)
        logging.debug(environment)

        conditions = (u'api={api}; environment={environment}'.format(api=api,
                                                                     environment=environment))

        matching_endpoints = [endpoint for _, endpoint in self.endpoints.iteritems()
                              if api in endpoint.apis and endpoint.environment == environment]

        return self.__single_endpoint(endpoints=matching_endpoints,
                                      conditions=conditions)

    def get_endpoint_for_request(self,
                                 url):

        logging.debug(url)
        best_match = - 1
        matched_endpoints = []

        for _, endpoint in self.endpoints.iteritems():
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

        for ep_name, endpoint in self.endpoints.iteritems():
            if hostname == ep_name:
                return endpoint.apis

        # If we get here we havent found a matching endpoint to return empty list
        return []

    def get_environment_for_host(self,
                                 hostname):

        matched_environments = set([endpoint.environment for ep_name, endpoint in self.endpoints.iteritems()
                                    if ep_name == hostname])

        if len(matched_environments) != 1:
            raise LookupError(u'Ambiguous environments for {hostname}'.format(hostname=hostname))

        return matched_environments.pop()

    def get_endpoint_apis(self):
        return {ep_name: endpoint.apis for ep_name, endpoint in self.endpoints.iteritems()}

    def get_endpoint_for_api_and_environment(self,
                                             api,
                                             environment):
        return [endpoint
                for _, endpoint in self.endpoints.iteritems()
                if api in endpoint.apis and endpoint.environment == environment]

    def get_endpoints_for_apis_and_environment(self,
                                               apis,
                                               environment):
        return [self.get_endpoint_for_api_and_environment(api=api, environment=environment) for api in apis]

    def get_endpoints_for_api(self,
                              api):

        endpoints = self.endpoints

        ep_list = []

        for ep_name, ep in endpoints.iteritems():
            if api in ep.apis:
                ep_list.append(ep_name)

        return ep_list

    def get_endpoints_for_environment(self,
                                      env):

        return self._cfg.find(ENDPOINTS_CONFIG, [(u'environment', env)]).keys()

    def get_endpoints_for_environment_and_api(self,
                                              api,
                                              env):
        api_ep = self.get_endpoints_for_api(api)
        env_ep = self.get_endpoints_for_environment(env)

        ep_list = []

        for ep in api_ep:
            if ep in env_ep:
                ep_list.append(ep)

        return ep_list
