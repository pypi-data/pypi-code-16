import logging
import json
import pika.spec as spec;

import fieldagent.rpc as rpc
import fieldagent.devicemanager as visa

class VisaRpcServer(rpc.RpcServer):
    def __init__(self, visa_library, username, password, name='visa_rpc_server', exchange="visa_rpc",
                 host='localhost'):
        rpc.RpcServer.__init__(self, name=name, host=host, exchange=exchange, username=username, password=password)
        self.device_manager = visa.VisaDeviceManager(visa_library=visa_library)

        self.create_method(name='alias', request_handler_method=self.on_alias_request)
        self.create_method(name='query', request_handler_method=self.on_query_request)
        self.create_method(name='read', request_handler_method=self.on_read_request)
        self.create_method(name='write', request_handler_method=self.on_write_request)
        self.create_method(name='list', request_handler_method=self.on_list_request)

    def on_alias_request(self, ch, method, props, body):
        props.content_type = 'application/json'
        props.type = 'hu.sagax.hedgehog.visa.M2mResponse'

        request = json.loads(body)

        try:
            response = self.device_manager.alias(request)
            logging.info('LOCAL.alias: ' + json.dumps(request) + ' -> ' + json.dumps(response))
            # return response
        except Exception as e:
            logging.error(e.message)
            response = {
                'result': e.message,
                # 'success': False
            }

        self.return_acknowledgement(ch=ch, method=method, props=props, response=response)

    def on_query_request(self, ch, method, props, body):
        props.content_type = 'application/json'
        props.type = 'hu.sagax.hedgehog.visa.M2mResponse'

        request = json.loads(body)

        try:
            response = self.device_manager.query(request)
            logging.info('LOCAL.query: ' + json.dumps(request) + ' -> ' + json.dumps(response))
        except Exception as e:
            logging.error(e.message)
            response = {
                'result': e.message,
                # 'success': False
            }

        self.return_acknowledgement(ch=ch, method=method, props=props, response=response)

    def on_write_request(self, ch, method, props, body):
        props.content_type = 'application/json'
        props.type = 'hu.sagax.hedgehog.visa.M2mResponse'

        request = json.loads(body)

        try:
            response = self.device_manager.write(request)
            logging.info('LOCAL.write: ' + json.dumps(request) + ' -> ' + json.dumps(response))
        except Exception as e:
            logging.error(e.message)
            response = {
                'message': e.message,
                'success': False
            }

        self.return_acknowledgement(ch=ch, method=method, props=props, response=response)

    def on_read_request(self, ch, method, props, body):
        props.content_type = 'application/json'
        props.type = 'hu.sagax.hedgehog.visa.M2mResponse'

        request = json.loads(body)

        try:
            response = self.device_manager.read(request)
            logging.info('LOCAL.read: ' + json.dumps(request) + ' -> ' + json.dumps(response))
        except Exception as e:
            logging.error(e.message)
            response = {
                'result': e.message,
                # 'success': False
            }

        self.return_acknowledgement(ch=ch, method=method, props=props, response=response)

    def on_list_request(self, ch, method, props, body):
        props.content_type = 'application/json'
        # props.type = 'hu.sagax.hedgehog.visa.M2mResponse'

        request = json.loads(body)

        try:
            response = self.device_manager.list(request)
            logging.info('LOCAL.list: ' + json.dumps(request) + ' -> ' + json.dumps(response))
        except Exception as e:
            logging.error(e.message)
            response = {
                'result': e.message,
                # 'success': False
            }

        self.return_acknowledgement(ch=ch, method=method, props=props, response=response)