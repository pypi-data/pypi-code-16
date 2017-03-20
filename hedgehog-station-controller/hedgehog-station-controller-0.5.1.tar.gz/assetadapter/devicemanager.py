from _ast import alias

import numpy
import pyvisa as visa
import logging
import datetime

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
        self.rm = visa.ResourceManager(visa_library)
        try:
            logging.info(self.rm.list_resources())
            self.devices = {}
        except Exception as ex:
            logging.exception("message")

    def alias(self, request):
        for key, value in request.items():
            try:
                self.devices[key] = self.rm.open_resource(value, read_termination='\n')
            except Exception as ex:
                logging.exception("message")
        return {
            'connectedDevices': len(request)
        }

    def query(self, request):
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

    def visa_query(self, alias, command):
        try:
            logging.info("VISA query on " + alias + ": " + command)
            resource = self.devices[alias]
            return resource.query_ascii_values(command, container=numpy.array, separator=',')
        except Exception as ex:
            logging.exception("message")

    def read(self, request):
        try:
            logging.info("dm.read", request)
            command = request['command']
            resource = self.devices[request['alias']]
            response = {
                'result': resource.read(command)
            }
            return response
        except Exception as ex:
            logging.exception("message")

    def write(self, request):
        try:
            logging.info("dm.write", request)
            command = request['command']
            resource = self.devices[request['alias']]
            resource.write(command)
        except Exception as ex:
            logging.exception("message")

    def list(self, request):
        try:
            logging.info("dm.list", request)
            return self.rm.list_resources()
        except Exception as ex:
            logging.exception("message")

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