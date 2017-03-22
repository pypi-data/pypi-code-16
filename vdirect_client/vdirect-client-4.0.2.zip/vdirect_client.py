import time
import json
import base64
import ssl
import socket
import platform
import sys
import urllib

ver = platform.python_version_tuple()
PY3 = int(ver[0]) >= 3
if PY3:
    import http.client as http
    import urllib.parse as urllib
else:
    import httplib as http
    import urllib
import logging


## ------------------------------------------------------------------------------------------------------------------
## Code was generated at Tue Mar 21 11:42:34 IST 2017
## vDirect version: 4.0.0
## Open issues:
## 1) Since the code is generated based on WADL it is not able to tell which of the query arguments is required
## ------------------------------------------------------------------------------------------------------------------

def _strict_status_codes(status_codes):
    sc = {}
    for key in status_codes.keys():
        if key not in sc.keys():
            sc[key] = []
        for code in status_codes[key]:
            if code / 100 not in [4, 5]:
                sc[key].append(code)
    return sc


def _non_strict_status_codes(status_codes):
    sc = {}
    for key in status_codes.keys():
        if key not in sc.keys():
            sc[key] = []
        for code in status_codes[key]:
           sc[key].append(code)
    return sc


STATUS_CODES = {
    'DELETE':[200,204,404,409],
    'GET':[200,400,404],
    'PUT':[200,204,400,404],
    'POST':[200,201,202,204, 400,404,409]
}

STRICT_STATUS_CODES = _strict_status_codes(STATUS_CODES)
NON_STRICT_STATUS_CODES = _non_strict_status_codes(STATUS_CODES)


RESP_STATUS = 0
RESP_REASON = 1
RESP_STR = 2
RESP_DATA = 3

_MOVED_PERMANENTLY = 301
_TEMPORARY_REDIRECT = 307
_REDIRECT_CODES = [_MOVED_PERMANENTLY,_TEMPORARY_REDIRECT]

class _SSLv23_Connection(http.HTTPSConnection):
    """Like HTTPSConnection but more specific"""
    def __init__(self, host, **kwargs):
        http.HTTPSConnection.__init__(self, host, **kwargs)

    def connect(self):
        """Overrides HTTPSConnection.connect to specify TLS version 1.2"""
        # Standard implementation from HTTPSConnection, which is not
        # designed for extension, unfortunately
        sock = socket.create_connection((self.host, self.port),
                self.timeout, self.source_address)
        if getattr(self, '_tunnel_host', None):
            self.sock = sock
            self._tunnel()

        # This is the only difference; default wrap_socket uses SSLv23
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                ssl_version=ssl.PROTOCOL_SSLv23)

class RestClientException(Exception):
    def __init__(self, status_code, failure_reason, http_verb, expected_codes = [], failure_msg = None, requested_url = None):
        self.status_code = status_code
        self.failure_reason = failure_reason
        self.http_verb = http_verb
        self.expected_codes = expected_codes
        self.failure_msg = failure_msg
        self.requested_url = requested_url
        try:
            self.message = "Operation failed: " + json.loads(failure_msg)['message']
        except Exception as e:
                    self.message = "Operation failed (during RestClientException exception creation): " + str(e)

    def __str__(self):
        return '{}. Status code: {}. Expected codes: {}. HTTP verb: {}. Failure msg: {}. Requested url: {} '.format(self.failure_reason,
                                                                                                   self.status_code,
                                                                                                   self.expected_codes,
                                                                                                   self.http_verb,
                                                                                                   self.failure_msg,
                                                                                                   self.requested_url)

class BadRequestException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(BadRequestException, self).__init__(400, failure_reason, http_verb, requested_url=resource)


class UnauthorizedException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(UnauthorizedException, self).__init__(401, failure_reason, http_verb, requested_url=resource)


class ForbiddenException(RestClientException):
    def __init__(self, resource,failure_reason='', http_verb='GET'):
        super(ForbiddenException, self).__init__(403, failure_reason, http_verb, requested_url=resource)


class NotFoundException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(NotFoundException, self).__init__(404, failure_reason, http_verb, requested_url=resource)


class MethodNotAllowedException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(MethodNotAllowedException, self).__init__(405, failure_reason, http_verb, requested_url=resource)


class NotAcceptableException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(NotAcceptableException, self).__init__(406, failure_reason, http_verb, requested_url=resource)


class ConflictException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(ConflictException, self).__init__(409, failure_reason, http_verb, requested_url=resource)


class UnsupportedMediaTypeException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(UnsupportedMediaTypeException, self).__init__(415, failure_reason, http_verb, requested_url=resource)


class InternalServerErrorException(RestClientException):
    def __init__(self, resource, failure_reason='', http_verb='GET'):
        super(InternalServerErrorException, self).__init__(500, failure_reason, http_verb, requested_url=resource)


EXCEPTIONS_MAPPING = {
    400: 'BadRequestException',
    401: 'UnauthorizedException',
    403: 'ForbiddenException',
    404: 'NotFoundException',
    405: 'MethodNotAllowedException',
    406: 'NotAcceptableException',
    409: 'ConflictException',
    415: 'UnsupportedMediaTypeException',
    500: 'InternalServerErrorException'
}


class RestClient(object):
    """
    :param vdirect_ip: string The primary / standalone vDirect server IP
    :param vdirect_user: string The vDirect user name
    :param vdirect_password: string The vDirect user password
    :param wait: bool Wait for async operation to complete [True]
    :param secondary_vdirect_ip: string The secondary vDirect server IP [None]
    :param https_port: int The https vDirect port [2189]
    :param http_port: int The http vDirect port [2188]
    :param timeout: int How many seconds to wait for async operation [60]
    :param https: bool Use https [True]
    :param strict_http_results: bool Throw exception for status codes 4xx,5xx or not [False]
    :param verify: bool SSL verification [True]
    """
    def __init__(self, vdirect_ip, vdirect_user, vdirect_password,wait=True,
                       secondary_vdirect_ip=None,https_port=2189,http_port=2188,
                       timeout=60,https=True,strict_http_results=False,
                       verify=True):
        
        def _handle_string_input(field_name, field_value):
            if PY3:
                return field_value
            else:
                if isinstance(field_value, unicode):
                    import unicodedata
                    return unicodedata.normalize('NFKD', field_value).encode('ascii', 'ignore')
                elif isinstance(field_value, str):
                    return field_value
                else:
                    raise Exception('Unsupported data type %s for %s. Expected data type: [str,unicode]' %
                                    (type(field_value), field_name))


        self.vdirect_ip = _handle_string_input('vdirect_ip', vdirect_ip)
        self.vdirect_user = _handle_string_input('vdirect_user', vdirect_user)
        self.vdirect_password = _handle_string_input('vdirect_password', vdirect_password)
        self.https = https
        self.wait = wait
        self.depth = 0
        self.max_depth = 20
        self.secondary_vdirect_ip = _handle_string_input('secondary_vdirect_ip', secondary_vdirect_ip) if secondary_vdirect_ip else None
        self.timeout= timeout
        self.verify = verify
        self.https_port = https_port
        self.http_port = http_port
        self.strict_http_results = strict_http_results
        self.base_uri = 'https://%s:%d/api/' % (self.vdirect_ip,self.https_port) if self.https else 'http://%s:%d/api/' % (self.vdirect_ip,self.http_port)
        if vdirect_user and vdirect_password:
            self.auth = '%s:%s' % (vdirect_user, vdirect_password)
            if PY3:
                 self.auth = base64.b64encode(self.auth.encode('utf-8'))
                 self.auth = self.auth.decode('utf-8').replace('\n','')
            else:
                self.auth = base64.encodestring(self.auth).replace('\n','')
        else:
            raise RuntimeError('No Username or Password were supplied')
        # ------------------------------------------------
        # see https://docs.python.org/2/library/ssl.html
        # ------------------------------------------------
        # Starting with Python 2.7.9, httplib and modules which use it,
        # such as urllib2 and xmlrpclib, default to verifying remote server certificates received
        # when establishing client HTTPS connections.
        # This default verification checks that the certificate is signed by a Certificate Authority in
        # the system trust store and that the Common Name (or Subject Alternate Name) on the presented certificate
        # matches the requested host.
        if self.verify and platform.python_version_tuple() < ('2','7','9'):
            ssl._https_verify_certificates()

        self.adc = ADC(self)
        self.appWall = AppWall(self)
        self.backup = Backup(self)
        self.container = Container(self)
        self.containerDriver = ContainerDriver(self)
        self.containerPool = ContainerPool(self)
        self.credentials = Credentials(self)
        self.defensePro = DefensePro(self)
        self.events = Events(self)
        self.ha = HA(self)
        self.icons = Icons(self)
        self.ipAddress = IpAddress(self)
        self.isl = ISL(self)
        self.managedObject = ManagedObject(self)
        self.message = Message(self)
        self.network = Network(self)
        self.obfuscate = Obfuscate(self)
        self.oper = Oper(self)
        self.rbac = RBAC(self)
        self.runnable = Runnable(self)
        self.scheduled = Scheduled(self)
        self.service = Service(self)
        self.session = Session(self)
        self.status = Status(self)
        self.template = Template(self)
        self.tenant = Tenant(self)
        self.triggered = Triggered(self)
        self.ui = UI(self)
        self.vrrp = VRRP(self)
        self.workflow = Workflow(self)
        self.workflowTemplate = WorkflowTemplate(self)

    def get_major_version(self):
        return 4

    def get_secondary_version(self):
        return 0

    def get_tertiary_version(self):
        return 0

    def get_version_tuple(self):
        return 4,0,0

    def _inc_depth(self):
        self.depth += 1

    def _dec_depth(self):
        self.depth -= 1

    def get_api_meta(self):
        return self._call('GET', '', {})

    def _call(self, action, resource,headers, wait=False, data=None, not_json=False):
        self._inc_depth()
        uri = resource if resource.startswith('http') else self.base_uri + resource
        body = data if not_json else json.dumps(data) if not isinstance(data,type(None)) else None
        if not headers:
            headers = {'Authorization': 'Basic %s' % self.auth}
        else:
            headers['Authorization'] = 'Basic %s' % self.auth
        if self.https:
            if self.verify:
                conn = http.HTTPSConnection (
                    self.vdirect_ip, port=self.https_port, timeout=self.timeout)
            else:
                conn = http.HTTPSConnection (
                    self.vdirect_ip, port=self.https_port, timeout=self.timeout,context=ssl._create_unverified_context())
            if conn is None:
                logging.error('vdirectRESTClient: Could not establish HTTPS '
                                     'connection')
                self._dec_depth()
                return 0, None, None, None
        else:
            conn = http.HTTPConnection(
                self.vdirect_ip, self.http_port, timeout=self.timeout)
            if conn is None:
                logging.error('vdirectRESTClient: Could not establish HTTP '
                                     'connection')
                self._dec_depth()
                return 0, None, None, None

        try:
            logging.debug('%s %s %s %s' % (action, uri, str(body), str(headers)))
            conn.request(action, uri, body, headers)
            response = conn.getresponse()
            if response.status in _REDIRECT_CODES:
                if not self.secondary_vdirect_ip:
                    raise Exception('Got redirect but secondary vDirect was not configured')
                peer = response.getheader('Location')
                start = peer.find('://')
                end = peer.rfind(':')
                peer = peer[start + 3:end]
                if peer != self.secondary_vdirect_ip:
                    raise Exception('Got redirect but secondary vDirect: %s is not the same as the peer: %s' % (self.secondary_vdirect_ip,peer))

            respstr = response.read()
            respdata = respstr
            try:
                respdata = json.loads(respstr.decode())
            except ValueError:
                # response was not JSON, ignore the exception
                pass
            ret = response.status, response.reason, respstr, respdata
        except Exception as e:
            log_dict = {'action': action, 'e': e}
            logging.error('vdirectRESTClient: %(action)s failure, %(e)r' %
                      log_dict)
            ret = -1, None, None, None
        conn.close()
        if ret[RESP_STATUS] in (0, -1):
            logging.warning('vDirect server is not responding (%s).' %
                self.vdirect_ip)
            ret = self._recover(action, resource,headers, wait, data, not_json)
        elif ret[RESP_STATUS] in _REDIRECT_CODES:
            logging.warning('vDirect server is not active (%s).' %
            self.vdirect_ip)
            ret = self._recover(action, resource,headers, wait, data, not_json)

        if self.wait and wait and ret[RESP_STATUS] == 202:
            complete = ret[RESP_DATA]['complete']
            if complete:
                self._dec_depth()
                return ret
            uri = ret[RESP_DATA]['uri']
            cnt = 0
            while cnt < self.timeout:
                time.sleep(1)
                cnt += 1
                ret = self._call('GET',uri,None,False)
                if ret[RESP_DATA]['complete']:
                    self._dec_depth()
                    return ret
            if cnt <= self.timeout:
                            msg = 'Timeout %s seconds is over and action wasn\'t completed' % self.timeout
                            return -1, 'timeout', msg, msg
            self._dec_depth()
            return ret
        else:
            self._dec_depth()
            return ret

    def _flip_servers(self):
        logging.warning('Fliping servers. Current is: {}, switching to {}'.format(self.vdirect_ip,self.secondary_vdirect_ip))
        self.vdirect_ip, self.secondary_vdirect_ip = self.secondary_vdirect_ip, self.vdirect_ip
        self.base_uri = 'https://%s:%d/api/' % (self.vdirect_ip,self.https_port) if self.https else 'http://%s:%d/api/' % (self.vdirect_ip,self.http_port)

    def _recover(self, action, resource,headers, wait, data, not_json):
        if self.vdirect_ip and self.secondary_vdirect_ip:
            if self.depth > self.max_depth:
                msg = 'Both vDirect servers: {} and {} are not responsive'.format(self.vdirect_ip,self.secondary_vdirect_ip)
                logging.error(msg)
                return -1, msg, None, None
            else:
                time.sleep(1)
                self._flip_servers()
                return self._call(action, resource,headers, wait, data, not_json)
        else:
            msg = 'REST client is not able to recover (since only one vDirect server is configured).'
            logging.error(msg)
            return -1, msg, None, None

    def _dict_to_query(self,d):
        query = ''
        for key in list(d.keys()):
            val = d.get(key)
            if val is not None:
                if isinstance(val, bool):
                    val = 'true' if val else 'false'
                query += key + '=' + urllib.quote(str(val)) + "&"
        return query[:-1]

    def _make_final_args(self,path_args,query_args):
        if query_args:
            path_args = path_args[:-1] if path_args.endswith('/') else path_args
            return path_args + '?' + query_args
        else:
           return path_args

    def _handle_result(self,http_verb,result,resource):
        if self.strict_http_results:
            if result[RESP_STATUS] in STRICT_STATUS_CODES[http_verb]:
                return result
            else:
                exception_clazz_name = EXCEPTIONS_MAPPING.get(result[RESP_STATUS])
                if exception_clazz_name:
                    current_module = sys.modules[__name__]
                    clazz = getattr(current_module, exception_clazz_name)
                    raise clazz(resource, failure_reason=result[RESP_STR], http_verb=http_verb)
                else:
                    raise RestClientException(result[RESP_STATUS], result[RESP_REASON], http_verb,
                                              STRICT_STATUS_CODES[http_verb], requested_url=resource,
                                              failure_msg=result[RESP_STR])
        else:
            if result[RESP_STATUS] in NON_STRICT_STATUS_CODES[http_verb]:
                return result
            else:
                raise RestClientException(result[RESP_STATUS],result[RESP_REASON],http_verb,NON_STRICT_STATUS_CODES[http_verb],requested_url=resource, failure_msg=result[RESP_STR])


class ADC():
    def __init__(self, client):
        self.client = client

    def run_template(self,data,adc_name,template=None):
        """
        :param template: string TBD
        :returns: application/vnd.com.radware.vdirect.template-result+json
        """
        args = {'template':template}
        path_args = 'adc/%s/config/' % (urllib.quote(adc_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.template-parameters+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update_groups(self,data,adc_name):
        """
        :returns: application/json
        """
        final_path = 'adc/%s/config/' % (urllib.quote(adc_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def control1(self,adc_name,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'adc/%s/config/' % (urllib.quote(adc_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def get_configuration(self,adc_name,diff=None,q=None,prop=None):
        """
        :param diff: string TBD
        :param q: string TBD
        :param prop: string TBD
        :returns: text/plain
        :returns: application/json
        """
        args = {'diff':diff,'q':q,'prop':prop}
        path_args = 'adc/%s/config/' % (urllib.quote(adc_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get(self,adc_name):
        """
        :returns: application/vnd.com.radware.vdirect.adc+json
        """
        final_path = 'adc/%s/' % (urllib.quote(adc_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def control_device(self,adc_name,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'adc/%s/device/' % (urllib.quote(adc_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,adc_name,configure_device=True):
        """
        :param configure_device: boolean TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        args = {'configureDevice':configure_device}
        path_args = 'adc/%s/' % (urllib.quote(adc_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.adc+json"},wait=True ,data=data)
        return self.client._handle_result('PUT',result,final_path)

    def control2(self,adc_name,reboot=None,action=None):
        """
        :param reboot: string TBD
        :param action: string TBD
        :returns: application/json
        """
        args = {'reboot':reboot,'action':action}
        path_args = 'adc/%s/' % (urllib.quote(adc_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def delete(self,adc_name,action='delete'):
        """
        :param action: string TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        args = {'action':action}
        path_args = 'adc/%s/' % (urllib.quote(adc_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('DELETE',final_path,{},wait=True )
        return self.client._handle_result('DELETE',result,final_path)

    def update_configuration(self,data,adc_name):
        """
        :returns: text/plain
        """
        final_path = 'adc/%s/config/' % (urllib.quote(adc_name))
        result = self.client._call('POST',final_path,{"Content-Type":"text/plain"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_configuration_last_captured(self,adc_name):
        """
        :returns: application/json
        """
        final_path = 'adc/%s/configLastCaptured/' % (urllib.quote(adc_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class AppWall():
    def __init__(self, client):
        self.client = client

    def get(self,app_wall_name):
        """
        :returns: application/vnd.com.radware.vdirect.appwall+json
        """
        final_path = 'appWall/%s/' % (urllib.quote(app_wall_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def control_device(self,app_wall_name,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'appWall/%s/device/' % (urllib.quote(app_wall_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def create(self,data,validate=None):
        """
        :param validate: string TBD
        :returns: application/vnd.com.radware.vdirect.appwall+json
        """
        args = {'validate':validate}
        path_args = 'appWall/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.appwall+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,app_wall_name):
        """
        """
        final_path = 'appWall/%s/' % (urllib.quote(app_wall_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.appwall+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def list(self):
        """
        :returns: application/vnd.com.radware.vdirect.appwall-list+json
        """
        final_path = 'appWall/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,app_wall_name):
        """
        """
        final_path = 'appWall/%s/' % (urllib.quote(app_wall_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Backup():
    def __init__(self, client):
        self.client = client

    def delete_backup(self,name):
        """
        """
        final_path = 'backup/%s/' % (urllib.quote(name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def restore(self,name,target=None):
        """
        :param target: string TBD
        :returns: application/json
        """
        args = {'target':target}
        path_args = 'backup/%s/' % (urllib.quote(name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def upload(self,data):
        """
        :returns: application/json
        """
        final_path = 'backup/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-zip-compressed"},data=data,not_json=True )
        return self.client._handle_result('POST',result,final_path)

    def clean_or_create(self,comment=None,target=None):
        """
        :param comment: string TBD
        :param target: string TBD
        :returns: application/json
        """
        args = {'comment':comment,'target':target}
        path_args = 'backup/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def get_archive(self,name):
        """
        :returns: application/x-zip-compressed
        """
        final_path = 'backup/%s/archive/' % (urllib.quote(name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list(self):
        """
        :returns: application/vnd.com.radware.vdirect.backup-list+json
        """
        final_path = 'backup/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_backup(self,name):
        """
        :returns: application/vnd.com.radware.vdirect.backup+json
        """
        final_path = 'backup/%s/' % (urllib.quote(name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class Container():
    def __init__(self, client):
        self.client = client

    def get(self,container_name):
        """
        :returns: application/vnd.com.radware.vdirect.container+json
        """
        final_path = 'container/%s/' % (urllib.quote(container_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create0(self,data,validate=None):
        """
        :param validate: string TBD
        :returns: application/vnd.com.radware.vdirect.container+json
        """
        args = {'validate':validate}
        path_args = 'container/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.container+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,container_name):
        """
        """
        final_path = 'container/%s/' % (urllib.quote(container_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.container+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def control(self,container_name,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'container/%s/device/' % (urllib.quote(container_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def create1(self,data,container_name,action='create'):
        """
        :param action: string TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        :returns: application/vnd.com.radware.vdirect.adc+json
        """
        args = {'action':action}
        path_args = 'container/%s/' % (urllib.quote(container_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.adc+json"},wait=True ,data=data)
        return self.client._handle_result('POST',result,final_path)

    def list(self,name=''):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.container-list+json
        """
        args = {'name':name}
        path_args = 'container/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,container_name):
        """
        """
        final_path = 'container/%s/' % (urllib.quote(container_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def list_adcs(self,container_name,name='',include_registered=None,include_unregistered=None,include_missing=None):
        """
        :param name: string TBD
        :param include_registered: boolean TBD
        :param include_unregistered: boolean TBD
        :param include_missing: boolean TBD
        :returns: application/vnd.com.radware.vdirect.adc-list+json
        """
        args = {'name':name,'includeRegistered':include_registered,'includeUnregistered':include_unregistered,'includeMissing':include_missing}
        path_args = 'container/%s/adc/' % (urllib.quote(container_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_supported_versions(self,container_name,name=None):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.alteon-version-list+json
        """
        args = {'name':name}
        path_args = 'container/%s/adcVersion/' % (urllib.quote(container_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_capacity(self,container_name):
        """
        :returns: application/vnd.com.radware.vdirect.container-capacity+json
        """
        final_path = 'container/%s/capacity/' % (urllib.quote(container_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class ContainerDriver():
    def __init__(self, client):
        self.client = client

    def get(self,name):
        """
        :returns: application/vnd.com.radware.vdirect.container-driver+json
        """
        final_path = 'containerDriver/%s/' % (urllib.quote(name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list(self):
        """
        :returns: application/vnd.com.radware.vdirect.container-driver-list+json
        """
        final_path = 'containerDriver/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list_parameters(self,name):
        """
        :returns: application/vnd.com.radware.vdirect.container-configuration-parameter-list+json
        """
        final_path = 'containerDriver/%s/parameters/' % (urllib.quote(name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class ContainerPool():
    def __init__(self, client):
        self.client = client

    def get(self,container_pool_name):
        """
        :returns: application/vnd.com.radware.vdirect.container-resource-pool+json
        """
        final_path = 'resource/containerPool/%s/' % (urllib.quote(container_pool_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.container-resource-pool+json
        """
        final_path = 'resource/containerPool/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.container-resource-pool+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,container_pool_name):
        """
        """
        final_path = 'resource/containerPool/%s/' % (urllib.quote(container_pool_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.container-resource-pool+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def list(self,name=''):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.container-resource-pool-list+json
        """
        args = {'name':name}
        path_args = 'resource/containerPool/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,container_pool_name):
        """
        """
        final_path = 'resource/containerPool/%s/' % (urllib.quote(container_pool_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def get_capacity(self,container_pool_name):
        """
        :returns: application/vnd.com.radware.vdirect.container-capacity+json
        """
        final_path = 'resource/containerPool/%s/capacity/' % (urllib.quote(container_pool_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class Credentials():
    def __init__(self, client):
        self.client = client

    def get_protocols(self,include_standard=False):
        """
        :param include_standard: boolean TBD
        :returns: application/json
        """
        args = {'includeStandard':include_standard}
        path_args = 'credentials/protocols/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list_credentials(self,service=None,protocol=None,host=None):
        """
        :param service: string TBD
        :param protocol: string TBD
        :param host: string TBD
        :returns: application/json
        """
        args = {'service':service,'protocol':protocol,'host':host}
        path_args = 'credentials/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update(self,data):
        """
        """
        final_path = 'credentials/'
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.credentials+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def create(self,data):
        """
        :returns: application/json
        """
        final_path = 'credentials/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.credentials+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_services(self,include_standard=False):
        """
        :param include_standard: boolean TBD
        :returns: application/json
        """
        args = {'includeStandard':include_standard}
        path_args = 'credentials/services/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self):
        """
        """
        final_path = 'credentials/'
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class DefensePro():
    def __init__(self, client):
        self.client = client

    def get(self,defense_pro_name):
        """
        :returns: application/vnd.com.radware.vdirect.defensepro+json
        """
        final_path = 'defensePro/%s/' % (urllib.quote(defense_pro_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def control_device(self,defense_pro_name,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'defensePro/%s/device/' % (urllib.quote(defense_pro_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,defense_pro_name):
        """
        """
        final_path = 'defensePro/%s/' % (urllib.quote(defense_pro_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.defensepro+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def create(self,data,validate=None):
        """
        :param validate: string TBD
        :returns: application/vnd.com.radware.vdirect.defensepro+json
        """
        args = {'validate':validate}
        path_args = 'defensePro/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.defensepro+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def list(self):
        """
        :returns: application/vnd.com.radware.vdirect.defensepro-list+json
        """
        final_path = 'defensePro/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,defense_pro_name):
        """
        """
        final_path = 'defensePro/%s/' % (urllib.quote(defense_pro_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Events():
    def __init__(self, client):
        self.client = client

    def postJSON_event(self,data,event_type=None):
        """
        :param event_type: string TBD
        """
        args = {'eventType':event_type}
        path_args = 'events/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def post_form_event(self,data,event_type=None):
        """
        :param event_type: string TBD
        """
        args = {'eventType':event_type}
        path_args = 'events/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def post_event(self):
        """
        """
        final_path = 'events/'
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)


class HA():
    def __init__(self, client):
        self.client = client

    def sleep(self,brb=None):
        """
        :param brb: long TBD
        """
        args = {'brb':brb}
        path_args = 'ha/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def set_ha_config(self,data):
        """
        """
        final_path = 'ha/config/'
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.ha-configuration+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def get_ha_status(self):
        """
        :returns: application/vnd.com.radware.vdirect.ha-status+json
        """
        final_path = 'ha/status/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def recover(self):
        """
        """
        final_path = 'ha/recover/'
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def get_ha_config(self):
        """
        :returns: application/vnd.com.radware.vdirect.ha-configuration+json
        """
        final_path = 'ha/config/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def is_active(self):
        """
        """
        final_path = 'ha/active/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def change_ha_status(self,data):
        """
        """
        final_path = 'ha/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.ha-status+json"},data=data)
        return self.client._handle_result('POST',result,final_path)


class Icons():
    def __init__(self, client):
        self.client = client

    def get_icon(self,name):
        """
        :returns: */*
        """
        final_path = 'icons/%s/' % (urllib.quote(name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class IpAddress():
    def __init__(self, client):
        self.client = client

    def release(self,ip_address_name,resource=None):
        """
        :param resource: string TBD
        """
        args = {'resource':resource}
        path_args = 'resource/ipAddress/%s/pool/' % (urllib.quote(ip_address_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def get(self,ip_address_name):
        """
        :returns: application/vnd.com.radware.vdirect.ip-pool+json
        """
        final_path = 'resource/ipAddress/%s/' % (urllib.quote(ip_address_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list2(self,ip_address_name,resource=None,owner=None):
        """
        :param resource: string TBD
        :param owner: string TBD
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        args = {'resource':resource,'owner':owner}
        path_args = 'resource/ipAddress/%s/pool/' % (urllib.quote(ip_address_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create5(self,name=None,start=None,end=None,gateway=None,mask=None):
        """
        :param name: string TBD
        :param start: string TBD
        :param end: string TBD
        :param gateway: string TBD
        :param mask: string TBD
        :returns: application/vnd.com.radware.vdirect.ip-pool+json
        """
        args = {'name':name,'start':start,'end':end,'gateway':gateway,'mask':mask}
        path_args = 'resource/ipAddress/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def acquire_from_form_data(self,data,ip_address_name):
        """
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        final_path = 'resource/ipAddress/%s/' % (urllib.quote(ip_address_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,ip_address_name):
        """
        """
        final_path = 'resource/ipAddress/%s/' % (urllib.quote(ip_address_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.ip-pool+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def acquire0(self,data,ip_address_name):
        """
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        final_path = 'resource/ipAddress/%s/' % (urllib.quote(ip_address_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.resource+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def create1(self,data,name=None):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.ip-pool+json
        """
        args = {'name':name}
        path_args = 'resource/ipAddress/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.ip-pool+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def list3(self,name=None,resource=None,owner=None):
        """
        :param name: string TBD
        :param resource: string TBD
        :param owner: string TBD
        :returns: application/vnd.com.radware.vdirect.ip-pool-list+json
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        """
        args = {'name':name,'resource':resource,'owner':owner}
        path_args = 'resource/ipAddress/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def acquire4(self,ip_address_name,comment=None,owner=None,reserve=False,resource=None):
        """
        :param comment: string TBD
        :param owner: string TBD
        :param reserve: boolean TBD
        :param resource: string TBD
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        args = {'comment':comment,'owner':owner,'reserve':reserve,'resource':resource}
        path_args = 'resource/ipAddress/%s/' % (urllib.quote(ip_address_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def delete(self,ip_address_name):
        """
        """
        final_path = 'resource/ipAddress/%s/' % (urllib.quote(ip_address_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class ISL():
    def __init__(self, client):
        self.client = client

    def release(self,isl_name,resource=None):
        """
        :param resource: string TBD
        """
        args = {'resource':resource}
        path_args = 'resource/isl/%s/pool/' % (urllib.quote(isl_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def list3(self,name=None,resource=None,owner=None):
        """
        :param name: string TBD
        :param resource: string TBD
        :param owner: string TBD
        :returns: application/vnd.com.radware.vdirect.isl-pool-list+json
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        """
        args = {'name':name,'resource':resource,'owner':owner}
        path_args = 'resource/isl/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get(self,isl_name):
        """
        :returns: application/vnd.com.radware.vdirect.isl-pool+json
        """
        final_path = 'resource/isl/%s/' % (urllib.quote(isl_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def acquire_from_form_data(self,data,isl_name):
        """
        :returns: application/vnd.com.radware.vdirect.resource+json
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        """
        final_path = 'resource/isl/%s/' % (urllib.quote(isl_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,isl_name):
        """
        """
        final_path = 'resource/isl/%s/' % (urllib.quote(isl_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.isl-pool+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def create1(self,data,name=None):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.isl-pool+json
        """
        args = {'name':name}
        path_args = 'resource/isl/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.isl-pool+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def create3(self,name=None,min='0',max='4095'):
        """
        :param name: string TBD
        :param min: string TBD
        :param max: string TBD
        :returns: application/vnd.com.radware.vdirect.isl-pool+json
        """
        args = {'name':name,'min':min,'max':max}
        path_args = 'resource/isl/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def acquire0(self,data,isl_name):
        """
        :returns: application/vnd.com.radware.vdirect.resource+json
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        """
        final_path = 'resource/isl/%s/' % (urllib.quote(isl_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.resource+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def list2(self,isl_name,resource=None,owner=None):
        """
        :param resource: string TBD
        :param owner: string TBD
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        args = {'resource':resource,'owner':owner}
        path_args = 'resource/isl/%s/pool/' % (urllib.quote(isl_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def acquire4(self,isl_name,comment=None,owner=None,reserve=False,resource=None):
        """
        :param comment: string TBD
        :param owner: string TBD
        :param reserve: boolean TBD
        :param resource: string TBD
        :returns: application/vnd.com.radware.vdirect.resource+json
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        """
        args = {'comment':comment,'owner':owner,'reserve':reserve,'resource':resource}
        path_args = 'resource/isl/%s/' % (urllib.quote(isl_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def delete(self,isl_name):
        """
        """
        final_path = 'resource/isl/%s/' % (urllib.quote(isl_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class ManagedObject():
    def __init__(self, client):
        self.client = client

    def get_object(self,type,name):
        """
        :returns: application/json
        """
        final_path = 'managed-object/%s/%s/' % (urllib.quote(type),urllib.quote(name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get(self,type=None,name=None,related=False,id=None):
        """
        :param type: string TBD
        :param name: string TBD
        :param related: boolean TBD
        :param id: string TBD
        :returns: application/json
        """
        args = {'type':type,'name':name,'related':related,'id':id}
        path_args = 'managed-object/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_id(self,type=None,name=None,id=None):
        """
        :param type: string TBD
        :param name: string TBD
        :param id: string TBD
        :returns: application/vnd.com.radware.vdirect.managed-object-id+json
        """
        args = {'type':type,'name':name,'id':id}
        path_args = 'managed-object/id/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list_objects(self,type):
        """
        :returns: application/json
        """
        final_path = 'managed-object/%s/' % (urllib.quote(type))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class Message():
    def __init__(self, client):
        self.client = client

    def get(self,message_id):
        """
        :returns: application/vnd.com.radware.vdirect.user-message+json
        """
        final_path = 'message/%s/' % (urllib.quote(message_id))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_message_entity(self,message_id):
        """
        :returns: application/octet-stream
        """
        final_path = 'message/%s/entity/' % (urllib.quote(message_id))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,message_id):
        """
        """
        final_path = 'message/%s/' % (urllib.quote(message_id))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def get_messages(self):
        """
        :returns: application/vnd.com.radware.vdirect.user-message-list+json
        """
        final_path = 'message/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class Network():
    def __init__(self, client):
        self.client = client

    def get(self,network_name):
        """
        :returns: application/vnd.com.radware.vdirect.network+json
        """
        final_path = 'resource/network/%s/' % (urllib.quote(network_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create(self,data,name=None):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.network+json
        """
        args = {'name':name}
        path_args = 'resource/network/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.network+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,network_name):
        """
        """
        final_path = 'resource/network/%s/' % (urllib.quote(network_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.network+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def list(self,name=None,vlan=None):
        """
        :param name: string TBD
        :param vlan: string TBD
        :returns: application/vnd.com.radware.vdirect.network-list+json
        """
        args = {'name':name,'vlan':vlan}
        path_args = 'resource/network/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,network_name):
        """
        """
        final_path = 'resource/network/%s/' % (urllib.quote(network_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Obfuscate():
    def __init__(self, client):
        self.client = client

    def get_obfuscated_string(self,val=None):
        """
        :param val: string TBD
        :returns: text/plain
        """
        args = {'val':val}
        path_args = 'obfuscate/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class Oper():
    def __init__(self, client):
        self.client = client

    def get_listeners(self):
        """
        :returns: application/vnd.com.radware.vdirect.syslog+json
        """
        final_path = 'oper/syslog/listener/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list_sessions(self):
        """
        :returns: application/json
        """
        final_path = 'oper/sessions/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def put_listeners(self,data):
        """
        """
        final_path = 'oper/syslog/listener/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.syslog+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_converters(self):
        """
        :returns: application/vnd.com.radware.vdirect.syslog+json
        """
        final_path = 'oper/syslog/converter/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def test(self,data,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'oper/syslog/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.syslog+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def set_log_level(self,level=None):
        """
        :param level: string TBD
        """
        args = {'level':level}
        path_args = 'oper/logs/server/level/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def auth_config(self):
        """
        """
        final_path = 'oper/auth/'
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def set_log_level_from_form_data(self,data):
        """
        """
        final_path = 'oper/logs/server/level/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def event_listener_config(self):
        """
        """
        final_path = 'oper/events/'
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def get_config(self):
        """
        :returns: application/json
        """
        final_path = 'oper/config/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_server_logs(self):
        """
        :returns: text/plain
        """
        final_path = 'oper/logs/server/preview/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def save_config(self,data):
        """
        """
        final_path = 'oper/config/'
        result = self.client._call('PUT',final_path,{"Content-Type":"application/json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def get_all_logs(self):
        """
        :returns: application/x-zip-compressed
        """
        final_path = 'oper/logs/server/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list_locks(self):
        """
        :returns: application/json
        """
        final_path = 'oper/locks/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def restart_server(self):
        """
        """
        final_path = 'oper/reset/'
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def get_services_table(self):
        """
        :returns: application/json
        """
        final_path = 'oper/service/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_last_message(self):
        """
        :returns: application/vnd.com.radware.vdirect.user-message+json
        """
        final_path = 'oper/message/last/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_workflows_table(self):
        """
        :returns: application/json
        """
        final_path = 'oper/workflow/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_log_level(self):
        """
        :returns: text/plain
        """
        final_path = 'oper/logs/server/level/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_adc_logs(self):
        """
        :returns: text/csv
        """
        final_path = 'oper/logs/adc/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list_device_locks(self):
        """
        :returns: application/json
        """
        final_path = 'oper/locks/device/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_json_server_logs(self):
        """
        :returns: application/vnd.com.radware.vdirect.message-log-list+json
        """
        final_path = 'oper/logs/server/preview/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def put_converters(self,data):
        """
        """
        final_path = 'oper/syslog/converter/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.syslog+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_licensed_capacity(self):
        """
        :returns: application/vnd.com.radware.vdirect.licensed-capacity-table+json
        """
        final_path = 'oper/adcLicense/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class RBAC():
    def __init__(self, client):
        self.client = client

    def list_users(self):
        """
        :returns: application/json
        """
        final_path = 'rbac/user/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get1(self,allowed_parent_of=None):
        """
        :param allowed_parent_of: string TBD
        :returns: application/vnd.com.radware.vdirect.role-list+json
        """
        args = {'allowedParentOf':allowed_parent_of}
        path_args = 'rbac/role/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list_groups(self):
        """
        :returns: application/json
        """
        final_path = 'rbac/group/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.role+json
        """
        final_path = 'rbac/role/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.role+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,role_name):
        """
        """
        final_path = 'rbac/role/%s/' % (urllib.quote(role_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.role+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def list_permissions(self,role=None,permission=None):
        """
        :param role: string TBD
        :param permission: string TBD
        :returns: application/json
        """
        args = {'role':role,'permission':permission}
        path_args = 'rbac/permission/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get0(self,role_name):
        """
        :returns: application/vnd.com.radware.vdirect.role+json
        """
        final_path = 'rbac/role/%s/' % (urllib.quote(role_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,role_name):
        """
        """
        final_path = 'rbac/role/%s/' % (urllib.quote(role_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Runnable():
    def __init__(self, client):
        self.client = client

    def get_available_actions(self,type,name):
        """
        :returns: application/json
        """
        final_path = 'runnable/%s/%s/' % (urllib.quote(type),urllib.quote(name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_action_info(self,type,name,action):
        """
        :returns: application/json
        """
        final_path = 'runnable/%s/%s/%s/' % (urllib.quote(type),urllib.quote(name),urllib.quote(action))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def run(self,data,type,name,action):
        """
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        final_path = 'runnable/%s/%s/%s/' % (urllib.quote(type),urllib.quote(name),urllib.quote(action))
        result = self.client._call('POST',final_path,{"Content-Type":"application/json"},wait=True ,data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_types(self):
        """
        :returns: application/json
        """
        final_path = 'runnable/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_runnable_objects(self,type):
        """
        :returns: application/json
        """
        final_path = 'runnable/%s/' % (urllib.quote(type))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_catalog(self):
        """
        :returns: application/json
        """
        final_path = 'runnable/catalog/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class Scheduled():
    def __init__(self, client):
        self.client = client

    def get(self,scheduled_name):
        """
        :returns: application/vnd.com.radware.vdirect.scheduled-job+json
        """
        final_path = 'scheduled/%s/' % (urllib.quote(scheduled_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update(self,data,scheduled_name):
        """
        """
        final_path = 'scheduled/%s/' % (urllib.quote(scheduled_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.scheduled-job+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def create(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.scheduled-job+json
        """
        final_path = 'scheduled/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.scheduled-job+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def control(self,scheduled_name,action=None):
        """
        :param action: string TBD
        """
        args = {'action':action}
        path_args = 'scheduled/%s/' % (urllib.quote(scheduled_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def list(self):
        """
        :returns: application/vnd.com.radware.vdirect.scheduled-job-list+json
        """
        final_path = 'scheduled/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,scheduled_name):
        """
        """
        final_path = 'scheduled/%s/' % (urllib.quote(scheduled_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Service():
    def __init__(self, client):
        self.client = client

    def delete_history(self,service_name):
        """
        """
        final_path = 'service/%s/history/' % (urllib.quote(service_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def get_history(self,service_name,format='json'):
        """
        :param format: string TBD
        :returns: text/plain
        :returns: application/vnd.com.radware.vdirect.log-message-list+json
        """
        args = {'format':format}
        path_args = 'service/%s/history/' % (urllib.quote(service_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def clean_history(self,name=None,tenant=None,clean=False):
        """
        :param name: string TBD
        :param tenant: string TBD
        :param clean: boolean TBD
        :returns: application/json
        """
        args = {'name':name,'tenant':tenant,'clean':clean}
        path_args = 'service/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def get_specification(self,service_name):
        """
        :returns: application/vnd.com.radware.vdirect.adc-service-specification+json
        """
        final_path = 'service/%s/specification/' % (urllib.quote(service_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update_service(self,data,service_name,action=None):
        """
        :param action: string TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        args = {'action':action}
        path_args = 'service/%s/' % (urllib.quote(service_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.adc-service+json"},wait=True ,data=data)
        return self.client._handle_result('POST',result,final_path)

    def delete_service(self,service_name):
        """
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        final_path = 'service/%s/' % (urllib.quote(service_name))
        result = self.client._call('DELETE',final_path,{},wait=True )
        return self.client._handle_result('DELETE',result,final_path)

    def run_action(self,service_name,action=None):
        """
        :param action: string TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        args = {'action':action}
        path_args = 'service/%s/' % (urllib.quote(service_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{},wait=True )
        return self.client._handle_result('POST',result,final_path)

    def get(self,service_name):
        """
        :returns: application/vnd.com.radware.vdirect.adc-service+json
        """
        final_path = 'service/%s/' % (urllib.quote(service_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create(self,data,name=None,tenant=None):
        """
        :param name: string TBD
        :param tenant: string TBD
        :returns: application/vnd.com.radware.vdirect.adc-service+json
        """
        args = {'name':name,'tenant':tenant}
        path_args = 'service/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.adc-service-specification+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def list(self,name='',include_deleted=False,deleted_only=False,using_resource_pool_name='',using_resource_pool_id=''):
        """
        :param name: string TBD
        :param include_deleted: boolean TBD
        :param deleted_only: boolean TBD
        :param using_resource_pool_name: string TBD
        :param using_resource_pool_id: string TBD
        :returns: application/vnd.com.radware.vdirect.adc-service-list+json
        """
        args = {'name':name,'includeDeleted':include_deleted,'deletedOnly':deleted_only,'usingResourcePoolName':using_resource_pool_name,'usingResourcePoolId':using_resource_pool_id}
        path_args = 'service/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update_specification(self,data,service_name):
        """
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        final_path = 'service/%s/specification/' % (urllib.quote(service_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.adc-service-specification+json"},wait=True ,data=data)
        return self.client._handle_result('PUT',result,final_path)

    def fix_service(self,data,service_name):
        """
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        final_path = 'service/%s/' % (urllib.quote(service_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.adc-service+json"},wait=True ,data=data)
        return self.client._handle_result('PUT',result,final_path)


class Session():
    def __init__(self, client):
        self.client = client

    def get(self,_cookie=None):
        """
        :param _cookie: string TBD
        :returns: application/vnd.com.radware.vdirect.session+json
        """
        args = {'Cookie':_cookie}
        path_args = 'session/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update(self,data,_cookie=None):
        """
        :param _cookie: string TBD
        """
        args = {'Cookie':_cookie}
        path_args = 'session/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.session+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def create(self,data,_cookie=None):
        """
        :param _cookie: string TBD
        :returns: application/vnd.com.radware.vdirect.session+json
        """
        args = {'Cookie':_cookie}
        path_args = 'session/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def delete(self,_cookie=None):
        """
        :param _cookie: string TBD
        :returns: */*
        """
        args = {'Cookie':_cookie}
        path_args = 'session/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Status():
    def __init__(self, client):
        self.client = client

    def get_result(self,token=None):
        """
        :param token: string TBD
        :returns: application/json
        """
        args = {'token':token}
        path_args = 'status/result/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_status(self,token=None):
        """
        :param token: string TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        args = {'token':token}
        path_args = 'status/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{},wait=True )
        return self.client._handle_result('GET',result,final_path)


class Template():
    def __init__(self, client):
        self.client = client

    def run_template(self,data,template_name):
        """
        :returns: application/vnd.com.radware.vdirect.template-result+json
        """
        final_path = 'template/%s/' % (urllib.quote(template_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.template-parameters+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def create_from_form_data(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.template+json
        """
        final_path = 'template/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def upload_source(self,data,template_name,fail_if_invalid=False):
        """
        :param fail_if_invalid: boolean TBD
        :returns: application/vnd.com.radware.vdirect.template+json
        """
        args = {'failIfInvalid':fail_if_invalid}
        path_args = 'template/%s/source/' % (urllib.quote(template_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('PUT',final_path,{"Content-Type":"text/x-velocity"},data=data,not_json=True )
        return self.client._handle_result('PUT',result,final_path)

    def upload_source_from_form_data(self,data,template_name):
        """
        :returns: application/vnd.com.radware.vdirect.template+json
        """
        final_path = 'template/%s/source/' % (urllib.quote(template_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def get(self,template_name):
        """
        :returns: application/vnd.com.radware.vdirect.template+json
        """
        final_path = 'template/%s/' % (urllib.quote(template_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update(self,data,template_name):
        """
        """
        final_path = 'template/%s/' % (urllib.quote(template_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.template+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def download_source(self,template_name):
        """
        :returns: text/x-velocity
        """
        final_path = 'template/%s/source/' % (urllib.quote(template_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create_from_source(self,data,name=None,tenant=None,fail_if_invalid=False):
        """
        :param name: string TBD
        :param tenant: string TBD
        :param fail_if_invalid: boolean TBD
        :returns: application/vnd.com.radware.vdirect.template+json
        """
        args = {'name':name,'tenant':tenant,'failIfInvalid':fail_if_invalid}
        path_args = 'template/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"text/x-velocity"},data=data,not_json=True )
        return self.client._handle_result('POST',result,final_path)

    def list(self,name='',display='summary',device=None):
        """
        :param name: string TBD
        :param display: string TBD
        :param device: string TBD
        :returns: application/vnd.com.radware.vdirect.template-list+json
        :returns: application/vnd.com.radware.Templates+xml
        """
        args = {'name':name,'display':display,'device':device}
        path_args = 'template/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,template_name):
        """
        """
        final_path = 'template/%s/' % (urllib.quote(template_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def get_icon(self,template_name):
        """
        :returns: application/json
        """
        final_path = 'template/%s/icon/' % (urllib.quote(template_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class Tenant():
    def __init__(self, client):
        self.client = client

    def get0(self,include=None):
        """
        :param include: string TBD
        :returns: application/vnd.com.radware.vdirect.tenant-list+json
        """
        args = {'include':include}
        path_args = 'tenant/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.tenant+json
        """
        final_path = 'tenant/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.tenant+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,tenant_name):
        """
        """
        final_path = 'tenant/%s/' % (urllib.quote(tenant_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.tenant+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def get1(self,tenant_name,include=None):
        """
        :param include: string TBD
        :returns: application/vnd.com.radware.vdirect.tenant+json
        """
        args = {'include':include}
        path_args = 'tenant/%s/' % (urllib.quote(tenant_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,tenant_name):
        """
        """
        final_path = 'tenant/%s/' % (urllib.quote(tenant_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Triggered():
    def __init__(self, client):
        self.client = client

    def control1(self,data,triggered_name,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'triggered/%s/' % (urllib.quote(triggered_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get(self,triggered_name):
        """
        :returns: application/vnd.com.radware.vdirect.triggered-job+json
        """
        final_path = 'triggered/%s/' % (urllib.quote(triggered_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.triggered-job+json
        """
        final_path = 'triggered/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.triggered-job+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,triggered_name):
        """
        """
        final_path = 'triggered/%s/' % (urllib.quote(triggered_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.triggered-job+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def control0(self,data,action=None):
        """
        :param action: string TBD
        :returns: application/json
        """
        args = {'action':action}
        path_args = 'triggered/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def control(self,triggered_name,action=None):
        """
        :param action: string TBD
        """
        args = {'action':action}
        path_args = 'triggered/%s/' % (urllib.quote(triggered_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def list(self):
        """
        :returns: application/vnd.com.radware.vdirect.triggered-job-list+json
        """
        final_path = 'triggered/'
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete(self,triggered_name):
        """
        """
        final_path = 'triggered/%s/' % (urllib.quote(triggered_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class UI():
    def __init__(self, client):
        self.client = client

    def get_resources3(self,data,url=None,ignore_cert=True,template_folder=None):
        """
        :param url: string TBD
        :param ignore_cert: boolean TBD
        :param template_folder: string TBD
        :returns: application/json
        """
        args = {'url':url,'ignoreCert':ignore_cert,'templateFolder':template_folder}
        path_args = 'ui/vsphere-assist/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_resources2(self,data,url=None,tenant=None):
        """
        :param url: string TBD
        :param tenant: string TBD
        :returns: application/json
        """
        args = {'url':url,'tenant':tenant}
        path_args = 'ui/openstack-assist/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_cron_expression_description(self,cron_expression=None):
        """
        :param cron_expression: string TBD
        :returns: text/plain
        """
        args = {'cronExpression':cron_expression}
        path_args = 'ui/scheduler-assist/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class VRRP():
    def __init__(self, client):
        self.client = client

    def release(self,vrrp_name,resource=None):
        """
        :param resource: string TBD
        """
        args = {'resource':resource}
        path_args = 'resource/vrrp/%s/pool/' % (urllib.quote(vrrp_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def list3(self,name=None,resource=None,owner=None):
        """
        :param name: string TBD
        :param resource: string TBD
        :param owner: string TBD
        :returns: application/vnd.com.radware.vdirect.vrrp-pool-list+json
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        """
        args = {'name':name,'resource':resource,'owner':owner}
        path_args = 'resource/vrrp/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get(self,vrrp_name):
        """
        :returns: application/vnd.com.radware.vdirect.vrrp-pool+json
        """
        final_path = 'resource/vrrp/%s/' % (urllib.quote(vrrp_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def acquire_from_form_data(self,data,vrrp_name):
        """
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        final_path = 'resource/vrrp/%s/' % (urllib.quote(vrrp_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-www-form-urlencoded"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def update(self,data,vrrp_name):
        """
        """
        final_path = 'resource/vrrp/%s/' % (urllib.quote(vrrp_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.vrrp-pool+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def create0(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.vrrp-pool+json
        """
        final_path = 'resource/vrrp/'
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.vrrp-pool+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def acquire0(self,data,vrrp_name):
        """
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        final_path = 'resource/vrrp/%s/' % (urllib.quote(vrrp_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.resource+json"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def create1(self,name=None):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.vrrp-pool+json
        """
        args = {'name':name}
        path_args = 'resource/vrrp/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def list2(self,vrrp_name,resource=None,owner=None):
        """
        :param resource: string TBD
        :param owner: string TBD
        :returns: application/vnd.com.radware.vdirect.resource-list+json
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        args = {'resource':resource,'owner':owner}
        path_args = 'resource/vrrp/%s/pool/' % (urllib.quote(vrrp_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def acquire4(self,vrrp_name,comment=None,owner=None,reserve=False,resource=None):
        """
        :param comment: string TBD
        :param owner: string TBD
        :param reserve: boolean TBD
        :param resource: string TBD
        :returns: application/vnd.com.radware.vdirect.resource+json
        """
        args = {'comment':comment,'owner':owner,'reserve':reserve,'resource':resource}
        path_args = 'resource/vrrp/%s/' % (urllib.quote(vrrp_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def delete(self,vrrp_name):
        """
        """
        final_path = 'resource/vrrp/%s/' % (urllib.quote(vrrp_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)


class Workflow():
    def __init__(self, client):
        self.client = client

    def update_workflow(self,data,workflow_name,action_name):
        """
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        final_path = 'workflow/%s/action/%s/' % (urllib.quote(workflow_name),urllib.quote(action_name))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.template-parameters+json"},wait=True ,data=data)
        return self.client._handle_result('POST',result,final_path)

    def delete_history(self,workflow_name):
        """
        """
        final_path = 'workflow/%s/history/' % (urllib.quote(workflow_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def get_workflow(self,workflow_name):
        """
        :returns: application/vnd.com.radware.vdirect.workflow+json
        """
        final_path = 'workflow/%s/' % (urllib.quote(workflow_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_history(self,workflow_name,format='json',debug=False):
        """
        :param format: string TBD
        :param debug: boolean TBD
        :returns: text/plain
        :returns: application/vnd.com.radware.vdirect.log-message-list+json
        """
        args = {'format':format,'debug':debug}
        path_args = 'workflow/%s/history/' % (urllib.quote(workflow_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def clean_history(self,clean=False):
        """
        :param clean: boolean TBD
        """
        args = {'clean':clean}
        path_args = 'workflow/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{})
        return self.client._handle_result('POST',result,final_path)

    def get_action_log(self,workflow_name):
        """
        :returns: application/vnd.com.radware.vdirect.action-log-list+json
        """
        final_path = 'workflow/%s/actionLog/' % (urllib.quote(workflow_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def delete_workflow(self,workflow_name,remove=False):
        """
        :param remove: boolean TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        args = {'remove':remove}
        path_args = 'workflow/%s/' % (urllib.quote(workflow_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('DELETE',final_path,{},wait=True )
        return self.client._handle_result('DELETE',result,final_path)

    def get_action_info(self,workflow_name,action_name):
        """
        :returns: application/vnd.com.radware.vdirect.workflow-parameters-info+json
        """
        final_path = 'workflow/%s/action/%s/' % (urllib.quote(workflow_name),urllib.quote(action_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_parameters(self,workflow_name):
        """
        :returns: application/vnd.com.radware.vdirect.template-parameters+json
        """
        final_path = 'workflow/%s/parameters/' % (urllib.quote(workflow_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def list(self,name='',type='',include_deleted=False,deleted_only=False,using_resource_name='',using_resource_id=''):
        """
        :param name: string TBD
        :param type: string TBD
        :param include_deleted: boolean TBD
        :param deleted_only: boolean TBD
        :param using_resource_name: string TBD
        :param using_resource_id: string TBD
        :returns: application/vnd.com.radware.vdirect.workflow-list+json
        """
        args = {'name':name,'type':type,'includeDeleted':include_deleted,'deletedOnly':deleted_only,'usingResourceName':using_resource_name,'usingResourceId':using_resource_id}
        path_args = 'workflow/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


class WorkflowTemplate():
    def __init__(self, client):
        self.client = client

    def get_descriptor(self,workflow_template_name):
        """
        :returns: application/xml
        """
        final_path = 'workflowTemplate/%s/descriptor/' % (urllib.quote(workflow_template_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def create_workflow(self,data,workflow_template_name,name=None):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.status+json
        """
        args = {'name':name}
        path_args = 'workflowTemplate/%s/' % (urllib.quote(workflow_template_name))
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.template-parameters+json"},wait=True ,data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_action_info(self,workflow_template_name,action_name):
        """
        :returns: application/vnd.com.radware.vdirect.workflow-parameters-info+json
        """
        final_path = 'workflowTemplate/%s/action/%s/' % (urllib.quote(workflow_template_name),urllib.quote(action_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update_archive(self,data,workflow_template_name):
        """
        """
        final_path = 'workflowTemplate/%s/archive/' % (urllib.quote(workflow_template_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/x-zip-compressed"},data=data,not_json=True )
        return self.client._handle_result('PUT',result,final_path)

    def list(self,name=''):
        """
        :param name: string TBD
        :returns: application/vnd.com.radware.vdirect.workflow-template-list+json
        """
        args = {'name':name}
        path_args = 'workflowTemplate/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def get_file(self,workflow_template_name,file_name):
        """
        :returns: application/json
        """
        final_path = 'workflowTemplate/%s/file/%s/' % (urllib.quote(workflow_template_name),urllib.quote(file_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update_workflow_template(self,data,workflow_template_name):
        """
        """
        final_path = 'workflowTemplate/%s/' % (urllib.quote(workflow_template_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/vnd.com.radware.vdirect.workflow-template+json"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def create_template(self,data):
        """
        :returns: application/vnd.com.radware.vdirect.workflow-template+json
        """
        final_path = 'workflowTemplate/'
        result = self.client._call('POST',final_path,{"Content-Type":"multipart/form-data"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_icon(self,workflow_template_name):
        """
        :returns: application/json
        """
        final_path = 'workflowTemplate/%s/icon/' % (urllib.quote(workflow_template_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update_file(self,data,workflow_template_name,file_name):
        """
        """
        final_path = 'workflowTemplate/%s/file/%s/' % (urllib.quote(workflow_template_name),urllib.quote(file_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"text/x-groovy"},data=data)
        return self.client._handle_result('PUT',result,final_path)

    def delete_workflow_template(self,workflow_template_name):
        """
        """
        final_path = 'workflowTemplate/%s/' % (urllib.quote(workflow_template_name))
        result = self.client._call('DELETE',final_path,{})
        return self.client._handle_result('DELETE',result,final_path)

    def create_template_from_descriptor(self,data,tenant=None,fail_if_invalid=False):
        """
        :param tenant: string TBD
        :param fail_if_invalid: boolean TBD
        :returns: application/vnd.com.radware.vdirect.workflow-template+json
        """
        args = {'tenant':tenant,'failIfInvalid':fail_if_invalid}
        path_args = 'workflowTemplate/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/xml"},data=data,not_json=True )
        return self.client._handle_result('POST',result,final_path)

    def create_template_from_archive(self,data,validate=False,fail_if_invalid=False,tenant=None):
        """
        :param validate: boolean TBD
        :param fail_if_invalid: boolean TBD
        :param tenant: string TBD
        :returns: application/vnd.com.radware.vdirect.workflow-template+json
        """
        args = {'validate':validate,'failIfInvalid':fail_if_invalid,'tenant':tenant}
        path_args = 'workflowTemplate/'
        final_path = self.client._make_final_args(path_args,self.client._dict_to_query(args))
        result = self.client._call('POST',final_path,{"Content-Type":"application/x-zip-compressed"},data=data,not_json=True )
        return self.client._handle_result('POST',result,final_path)

    def update_descriptor(self,data,workflow_template_name):
        """
        """
        final_path = 'workflowTemplate/%s/descriptor/' % (urllib.quote(workflow_template_name))
        result = self.client._call('PUT',final_path,{"Content-Type":"application/xml"},data=data,not_json=True )
        return self.client._handle_result('PUT',result,final_path)

    def get_archive(self,workflow_template_name):
        """
        :returns: application/x-zip-compressed
        """
        final_path = 'workflowTemplate/%s/archive/' % (urllib.quote(workflow_template_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)

    def update_template(self,data,workflow_template_name):
        """
        """
        final_path = 'workflowTemplate/%s/archive/' % (urllib.quote(workflow_template_name))
        result = self.client._call('POST',final_path,{"Content-Type":"multipart/form-data"},data=data)
        return self.client._handle_result('POST',result,final_path)

    def get_workflow_template(self,workflow_template_name):
        """
        :returns: application/vnd.com.radware.vdirect.workflow-template+json
        """
        final_path = 'workflowTemplate/%s/' % (urllib.quote(workflow_template_name))
        result = self.client._call('GET',final_path,{})
        return self.client._handle_result('GET',result,final_path)


