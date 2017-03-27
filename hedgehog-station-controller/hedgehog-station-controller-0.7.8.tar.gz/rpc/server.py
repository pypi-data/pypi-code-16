import json
import logging
import pika

import assetadapter.devicemanager as dm
import rpc

import schedule
import time
import uuid
import datetime

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

        self.create_method(name='close', request_handler_method=self.on_close_channel)
        logging.info('- Registrate consumer method LOCAL.close_channel')

        self.data_channels = []
        self.synchInterval = 3

    def on_list_request(self, ch, method, props, body):
        response = []

        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.list(request)
            logging.info('LOCAL.list: ' + json.dumps(request) + ' -> ' + json.dumps(response))

        except dm.ScVisaError as ex:
            logging.warning('Exception happened on LOCAL.list ' + str(ex))
            self.send_event(body={
                'error': ex.toJSON(),
                'request': body
            })
        except Exception as e:
            logging.error(e)
        finally:
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)

    def on_alias_request(self, ch, method, props, body):
        response = {}
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.alias(request)
            logging.info('LOCAL.alias: ' + json.dumps(request) + ' -> ' + json.dumps(response))
        except dm.ScVisaError as ex:
            logging.warning('Exception happened on LOCAL.alias ' + str(ex))
            self.send_event(body={
                'error': ex.toJSON(),
                'request': body
            })

        except Exception as e:
            logging.error(e)
        finally:
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)

    def on_query_request(self, ch, method, props, body):
        response = {
            'result': None
        }
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.query(request)
            logging.info('LOCAL.query: ' + json.dumps(request) + ' -> ' + json.dumps(response)[:20] + ' ...')

        except dm.ScVisaError as ex:
            logging.warning('Exception happened on LOCAL.query ' + str(ex))
            self.send_event(body={
                'error': ex.toJSON(),
                'request': body
            })
        except Exception as e:
            logging.error(e)
        finally:
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response, headers={
                '__TypeId__': 'hu.sagax.hedgehog.visa.M2mResponse'
            })

    def on_write_request(self, ch, method, props, body):
        response = {}
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.write(request)
            logging.info('LOCAL.write: ' + json.dumps(request) + ' -> ' + json.dumps(response)[:20] + ' ...')

        except dm.ScVisaError as ex:
            logging.warning('Exception happened on LOCAL.write ' + str(ex))
            self.send_event(body={
                'error': ex.toJSON(),
                'request': body
            })
        except Exception as e:
            logging.warning('Exception happened on LOCAL.write ...')
            logging.error(e)
        finally:
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response)

    def on_read_request(self, ch, method, props, body):
        response = {
            'result': None
        }
        try:
            request = json.loads(body.decode("utf-8"))
            response = self.device_manager.read(request)
            logging.info('LOCAL.read: ' + json.dumps(request) + ' -> ' + json.dumps(response)[:20] + ' ...')

        except dm.ScVisaError as ex:
            logging.warning('Exception happened on LOCAL.read ' + str(ex))
            self.send_event(body={
                'error': ex.toJSON(),
                'request': body
            })
        except Exception as e:
            logging.error(e)
        finally:
            self.return_acknowledgement(ch=ch, method=method, props=props, response=response, headers={
                '__TypeId__': 'hu.sagax.hedgehog.visa.M2mResponse'
            })

    def on_execute(self, channel, method, props, body):
        request = json.loads(body.decode("utf-8"))
        response = {}
        # for command in request['setup']:
        try:
            self.data_channels.append(request)


            request['job'] = str(uuid.uuid4())

            response = {
                'executed': True,
                'sampling': self.synchInterval,
                'domain': request['domain'],
                'job': str(uuid.uuid4()),
                'controller': platform.node()
            }

            if ('period' in request):
                schedule.every(request['period']).seconds.do(self.tick_job, request['alias'], request['domain'],
                                                             request['command']).tag(request['job'])
            else:
                schedule.every(self.synchInterval).seconds.do(self.tick_job, request['alias'], request['domain'],
                                                              request['command']).tag(request['job'])

            logging.info('LOCAL.execute: ' + json.dumps(
                request) + ' opened new channel with sampling in ' + str(request['period']) + ' ms.')


        except dm.ScVisaError as ex:
            logging.warning('Exception happened on LOCAL.execute ' + str(ex))
            self.send_event(body={
                'error': ex.toJSON(),
                'request': body
            })

            response = {
                'executed': False
            }
        except Exception as ex:
            logging.error(ex)

            response = {
                'executed': False
            }
        finally:
            self.return_acknowledgement(ch=channel, method=method, props=props, response=response, headers={
                '__TypeId__': 'hu.sagax.hedgehog.visa.M2mStreamResponse'
            })

    def on_close_channel(self, channel, method, props, body):
        request = json.loads(body.decode("utf-8"))
        response = {}
        # for command in request['setup']:
        try:
            response['domain'] = request['domain']
            response['controller'] = platform.node()

            if ('job' in request):
                for ch in self.data_channels:
                    if ch['job'] == request['job']:
                        self.data_channels.remove(request)

                logging.info('LOCAL.close: ' + json.dumps(request) + ' close.')

                schedule.clear(request['job'])
                response['job'] = request['job']

            else:
                self.data_channels = []
                for job in schedule.jobs:
                    schedule.cancel_job(job)

            response['executed'] = True

        except Exception as e:
            response={
                'executed': False
            }

            logging.error(e)
            self.send_event(body={
                'error': e,
                'request': body
            })
        finally:
            self.return_acknowledgement(ch=channel, method=method, props=props, response=response, headers={
                '__TypeId__': 'hu.sagax.hedgehog.visa.M2mStreamResponse'
            })

    def tick_job(self, alias, domain, command):
        response = {}
        try:
            response = self.device_manager.visa_query(alias=alias, command=command).tolist()
            logging.info('LOCAL.query: ' + command + ' -> ' + json.dumps(response)[:20] + ' ...')
            self.send_data(alias=alias, domain=domain, timestamp=datetime.datetime.now(), value=response)
        except dm.ScVisaError as ex:
            logging.warning('Exception happened on tick query ' + str(ex))
            self.send_event(body={
                'error': ex.toJSON()
            })
        except Exception as ex:
            logging.error(ex)
            self.send_event(body={
                'error': ex
            })

    def send_data(self, alias, domain, value, timestamp):
        message_properties = pika.BasicProperties(content_type='application/json', content_encoding='utf-8', headers={
            'alias': alias,
            'domain': domain,
            'controller': platform.node()
        })
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key='ingestion',
            properties=message_properties,
            body=json.dumps(obj={
                'timestamp': str(timestamp),
                'value': value
            }, ensure_ascii=False))
        logging.debug('Call \"' + "ingestion" + '\" request ' + str(value) + ' -> ' + str(message_properties))

    def send_event(self, body):
        message_properties = pika.BasicProperties(content_type='application/json', content_encoding='utf-8', headers={
            'controller': platform.node()
        })
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key='log',
            properties=message_properties,
            body=json.dumps(body))
        logging.debug('Call \"' + "log" + '\" request ' + str(body) + ' -> ' + str(message_properties))
