import logging

import pika

import pyvisa as visa
import logging


class VisaDeviceManager():
    def __init__(self, visa_library):
        self.rm = visa.ResourceManager(visa_library)
        try:
            logging.info(self.rm.list_resources())
            self.devices = {}
        except Exception as ex:
            logging.exception("message")

    def alias(self, request):
        for key, value in request.iteritems():
            try:
                self.devices[key] = self.rm.open_resource(value, read_termination='\n')
            except Exception as ex:
                logging.exception("message")
        return {
            'connectedDevices': len(request)
        }

    def query(self, request):
        try:
            command = request['command']
            resource = self.devices[request['alias']]
            response = {
                'result': resource.query(command)
            }
            return response
        except Exception as ex:
            logging.exception("message")

    def read(self, request):
        try:
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
            command = request['command']
            resource = self.devices[request['alias']]
            resource.write(command)
        except Exception as ex:
            logging.exception("message")

    def list(self, request):
        try:
            return self.rm.list_resources()
        except Exception as ex:
            logging.exception("message")
