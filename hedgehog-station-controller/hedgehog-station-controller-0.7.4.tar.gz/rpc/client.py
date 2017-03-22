import json
import logging

import rpc.rpc as rpc


class VisaRpcClient(rpc.RpcClient):
    def __init__(self, username, password, name='query', exchange='visa_rpc', host='localhost', port=5432):
        rpc.RpcClient.__init__(self, host=host, name=name, exchange=exchange, username=username, password=password, port=port)
        self.name = name
        self.declare_method(self.on_response)

    def alias(self, request):
        logging.info('REMOTE.alias request ' + json.dumps(obj=request, ensure_ascii=False))
        return self.call(body=request, method_name='alias')

    def query(self, request):
        logging.info('REMOTE.query request ' + json.dumps(obj=request, ensure_ascii=False))
        return self.call(body=request, method_name='query')

    def read(self, request):
        logging.info('REMOTE.read request ' + json.dumps(obj=request, ensure_ascii=False))
        return self.call(body=request, method_name='read')

    def write(self, request):
        logging.info('REMOTE.write request ' + json.dumps(obj=request, ensure_ascii=False))
        return self.call(body=request, method_name='write')

    def list(self, request):
        logging.info('REMOTE.list request ' + json.dumps(obj=request, ensure_ascii=False))
        return self.call(body=request, method_name='list')
