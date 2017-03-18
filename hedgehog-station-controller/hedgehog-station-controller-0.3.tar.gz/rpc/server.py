import json
import logging
import pika

import assetadapter.devicemanager as dm
import rpc.rpc as rpc

import schedule
import time

import platform

schedule.run_continuously(interval=1)


def globalTick():
    print('Synchronization begins ...')

    print('Synchronization ended.')

# schedule.every(10).seconds.do(globalTick)

class VisaRpcServer(rpc.RpcServer):
    def __init__(self, visa_library, username, password, name='visa_rpc_server', exchange="visa_rpc",
                 host='localhost'):
        rpc.RpcServer.__init__(self, name=name, host=host, exchange=exchange, username=username, password=password)
        self.device_manager = dm.VisaDeviceManager(visa_library=visa_library)

        self.create_method(name='alias', request_handler_method=self.on_alias_request)
        logging.info('- Registrate consumer method LOCAL.alias')

        self.create_method(name='query', request_handler_method=self.on_query_request)
        logging.info('- Registrate consumer method LOCAL.query')

        self.create_method(name='read', request_handler_method=self.on_read_request)
        logging.info('- Registrate consumer method LOCAL.read')

        self.create_method(name='write', request_handler_method=self.on_write_request)
        logging.info('- Registrate consumer method LOCAL.write')

        self.create_method(name='list', request_handler_method=self.on_list_request)
        logging.info('- Registrate consumer method LOCAL.list')

        self.create_method(name='execution', request_handler_method=self.on_execute)
        logging.info('- Registrate consumer method LOCAL.exec')

        self.data_channels = []
        self.synchInterval = 3

    def on_list_request(self, ch, method, props, body):
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.list(request)
            logging.info('LOCAL.list: ' + json.dumps(request) + ' -> ' + json.dumps(response))
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)
        except Exception as e:
            logging.warning('Exception happened on LOCAL.list ...')
            logging.error(e)

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

    def on_execute(self, channel, method, props, body):
        request = json.loads(body.decode("utf-8"))
        # for command in request['setup']:
        try:
            self.data_channels.append(request)
            logging.info('LOCAL.execute: ' + json.dumps(
                request) + ' opened new channel with sampling in ' + str(self.synchInterval) + ' ms.')


            self.return_acknowledgement(ch=channel, method=method, props=props, response={
                'executed': True,
                'sampling': self.synchInterval
            })

            schedule.every(self.synchInterval).seconds.do(self.tick_job)
            # schedule.every(self.synchInterval).seconds.do(globalTick)


        except Exception as e:

            self.return_acknowledgement(ch=channel, method=method, props=props, response={
                'executed': False
            })

            logging.warning(e)
            self.send_event(body={
                'error': e,
                'request': body
            })

    def tick_job(self):
        logging.info('TICK ------------------------------------------------------------------')
        for ch in self.data_channels:
            try:
                response = self.device_manager.query(ch)
                logging.info('LOCAL.query: ' + json.dumps(ch) + ' -> ' + json.dumps(response))
                self.send_data(alias=response['alias'], domain=ch['command'], body=response)
            except Exception as e:
                logging.warning('Exception tick query ' + ch['command'] + ' ...')
                logging.error(e)
                self.send_event(body=e)

    def send_data(self, alias, domain, body):
        message_properties = pika.BasicProperties(content_type='application/json', content_encoding='utf-8', headers={
            'alias': alias,
            'domain': domain,
            'controller': platform.node()
        })
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key='ingestion',
            properties=message_properties,
            body=json.dumps(obj=body, ensure_ascii=False))
        logging.debug('Call \"' + "ingestion" + '\" request ' + str(body) + ' -> ' + str(message_properties))

    def send_event(self, body):
        message_properties = pika.BasicProperties(content_type='application/json', content_encoding='utf-8', headers={
            'controller': platform.node()
        })
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key='log',
            properties=message_properties,
            body=body)
        logging.debug('Call \"' + "ingestion" + '\" request ' + str(body) + ' -> ' + str(message_properties))
