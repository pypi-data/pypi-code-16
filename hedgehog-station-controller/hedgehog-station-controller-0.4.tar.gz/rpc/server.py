import json
import logging

import assetadapter.devicemanager as dm
import rpc.rpc as rpc


class VisaRpcServer(rpc.RpcServer):
    def __init__(self, visa_library, username, password, name='visa_rpc_server', exchange="visa_rpc",
                 host='localhost'):
        rpc.RpcServer.__init__(self, name=name, host=host, exchange=exchange, username=username, password=password)
        self.device_manager = dm.VisaDeviceManager(visa_library=visa_library)

        self.create_method(name='alias', request_handler_method=self.on_alias_request)
        self.create_method(name='query', request_handler_method=self.on_query_request)
        self.create_method(name='read', request_handler_method=self.on_read_request)
        self.create_method(name='write', request_handler_method=self.on_write_request)
        self.create_method(name='list', request_handler_method=self.on_list_request)

    def on_alias_request(self, ch, method, props, body):
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.alias(request)
            logging.info('LOCAL.alias: ' + json.dumps(request) + ' -> ' + json.dumps(response))
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)
        except Exception as e:
            logging.warning('Exception happened on LOCAL.alias ...')
            logging.error(e)

    def on_query_request(self, ch, method, props, body):
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.query(request)
            logging.info('LOCAL.query: ' + json.dumps(request) + ' -> ' + json.dumps(response))
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)
        except Exception as e:
            logging.warning('Exception happened on LOCAL.query ...')
            logging.error(e)

    def on_write_request(self, ch, method, props, body):
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.write(request)
            logging.info('LOCAL.write: ' + json.dumps(request) + ' -> ' + json.dumps(response))
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)
        except Exception as e:
            logging.warning('Exception happened on LOCAL.write ...')
            logging.error(e)

    def on_read_request(self, ch, method, props, body):
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.read(request)
            logging.info('LOCAL.read: ' + json.dumps(request) + ' -> ' + json.dumps(response))
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)
        except Exception as e:
            logging.warning('Exception happened on LOCAL.read ...')
            logging.error(e)

    def on_list_request(self, ch, method, props, body):
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.list(request)
            logging.info('LOCAL.list: ' + json.dumps(request) + ' -> ' + json.dumps(response))
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)
        except Exception as e:
            logging.warning('Exception happened on LOCAL.list ...')
            logging.error(e)