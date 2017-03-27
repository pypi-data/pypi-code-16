from _ast import alias

import numpy
import pyvisa as visa
import logging
import datetime
import json
import threading

class ScVisaError(Exception):
    def __init__(self, message):
        self.ts = str(datetime.datetime.now())
        self.message = message
    def __str__(self):
        return '%s: %s' % (self.ts, self.message)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class VisaCommandExecutionError(Exception):
    def __init__(self, alias, address, request, response):
        self.request = request
        self.response = response
        self.address = address
        self.alias = alias
        self.ts = datetime.datetime.now()

    def __str__(self):
        return '%s[%s]: %s -> %s' % (self.alias, self.address, self.request, self.response)

class ResponseBuilder:

    def __init__(self, response={}):
        self.message = response
        self.results = [],
        self.errors = []

    def alias(self, count):
        self.results.append({
            'connectedDevices': count
        })

    def success(self, ts, request, response):
        self.results.append({
            'ts': ts,
            'request': request,
            'response': response
        })
        return self

    def error(self, errorcode, message):
        self.errors.append({
            'error': errorcode,
            'message': message
        })
        return self

    def build(self):
        self.message.results = self.results
        self.message.errors = self.errors
        return self.message

class VisaDeviceManager():
    def __init__(self, visa_library):
        self.lock = threading.Lock()
        self.rm = visa.ResourceManager(visa_library)

        self.lock.acquire()
        try:
            logging.info(self.rm.list_resources())
            self.devices = {}
        except Exception as ex:
            logging.exception("message")
            raise ScVisaError(str(ex))
        finally:
            self.lock.release()

    def alias(self, request):
        index = len(request)
        self.lock.acquire()
        try:
            logging.info('dm.alias: onnectiong devices ...')
            for key, value in request.items():
                try:
                    if any(value in s for s in self.rm.list_resources()):
                    # res = self.rm.open_resource(value, read_termination='\n')
                        res = self.rm.open_resource(value)
                        logging.info('<' + key + '> : ' + value)
                        self.devices[key] = res
                        index += 1
                except Exception as ex:
                    logging.exception("message")
            return {
                'connectedDevices': index
            }
        finally:
            self.lock.release()

    def query(self, request):
        self.lock.acquire()
        try:
            logging.info("dm.query" + str(request))
            command = request['command']
            resource = self.devices[request['alias']]
            response = {
                'result': resource.query(command)
            }
            return response
        except Exception as ex:
            logging.exception("message")
            raise ScVisaError(str(ex))
        finally:
            self.lock.release()

    def visa_query(self, alias, command):
        self.lock.acquire()
        try:
            logging.info("VISA query on " + alias + ": " + command)
            resource = self.devices[alias]
            return resource.query_ascii_values(command, container=numpy.array, separator=',')
            # return resource.query_ascii_values(command, container=[], separator=',', delay=1)
        except Exception as ex:
            logging.exception("message")
            raise ScVisaError(str(ex))
        finally:
            self.lock.release()

    def read(self, request):
        self.lock.acquire()
        try:
            logging.info("dm.read" + str(request))
            command = request['command']
            resource = self.devices[request['alias']]
            response = {
                'result': resource.read(command)
            }
            return response
        except Exception as ex:
            logging.exception("message")
            raise ScVisaError(str(ex))
        finally:
            self.lock.release()

    def write(self, request):
        self.lock.acquire()
        try:
            logging.info("dm.write" + str(request))
            command = request['command']
            resource = self.devices[request['alias']]
            resource.write(command)
        except Exception as ex:
            logging.exception("message")
            raise ScVisaError(str(ex))
        finally:
            self.lock.release()

    def list(self, request):
        self.lock.acquire()
        try:
            logging.info("dm.list", request)
            return self.rm.list_resources()
        except Exception as ex:
            logging.exception("message")
            raise ScVisaError(str(ex))
        finally:
            self.lock.release()
            # def query(self, alias, command):
    #     try:
    #         resource = self.devices[alias]
    #         response = resource.query(command)
    #         logging.info("visa query on resource %: %s", alias, command)
    #         return response
    #     except Exception as ex:
    #         logging.exception("message")
    #         raise VisaCommandExecutionError(alias=alias, address=resource._resource_name, request=command, response=ex)

    # def execute(self, alias, command):
    #     builder = ResponseBuilder()
    #
    #     try:
    #         resource = self.devices[alias]
    #     except Exception as ex:
    #         logging.exception("message")
    #         raise VisaCommandExecutionError(alias=alias, address=resource._resource_name, request=command, response=ex)
    #
    #     for command in command_sequence:
    #         try:
    #             result = resource.query(command)
    #             logging.info("visa query on resource %: %s", alias, command)
    #             builder.success()
    #         except Exception as e:
    #             logging.warning("visa query on resource %: %s", alias, command)
    #             builder.error(errorcode=0, message=str(e))
    #
    #     return builder.build()