from __future__ import unicode_literals

import logging
from ctypes import *
import ctypes.util


class BusId(Structure):
    _fields_ = [
        ('type', c_short),
        ('nr', c_short),
    ]

    def to_python(self, reader):
        adapter_name = bytes(reader.sensors_get_adapter_name(byref(self))).decode()

        return {
            'type': int(self.type),
            'nr': int(self.nr),
            'adapter_name': adapter_name if adapter_name else None
        }


class ChipName(Structure):
    _fields_ = [
        ('prefix', c_char_p),
        ('sensors_bus_id', BusId),
        ('addr', c_int),
        ('path', c_char_p),
    ]

    def to_python(self, reader):
        return {
            'prefix': bytes(self.prefix).decode(),
            'sensors_bus_id': self.sensors_bus_id.to_python(reader),
            'addr': int(self.addr),
            'path': bytes(self.path).decode(),
        }


class SensorsFeature(Structure):
    _fields_ = [
        ('name', c_char_p),
        ('number', c_int),
        ('type', c_int),
        ('first_subfeature', c_int),
        ('padding1', c_int),
    ]

    def to_python(self, reader):
        return {
            'name': bytes(self.name).decode(),
            'number': int(self.number),
            'type': int(self.type),
            'first_subfeature': int(self.first_subfeature),
            'padding1': int(self.padding1),
        }


class SensorsSubFeature(Structure):
    _fields_ = [
        ('name', c_char_p),
        ('number', c_int),
        ('type', c_int),
        ('mapping', c_int),
        ('flags', c_uint),
    ]

    def to_python(self, reader):
        return {
            'name': bytes(self.name).decode(),
            'number': int(self.number),
            'type': int(self.type),
            'mapping': int(self.mapping),
            'flags': int(self.flags),
        }


def log_wrapper(func, restype):
    def wrapper(*args, **kwargs):
        logging.debug('Calling {}...'.format(func.__name__))

        func.restype = restype
        return func(*args, **kwargs)
    return wrapper


class SensorsReader:
    class Error(Exception):
        pass

    class ParseError(Error):
        def __init__(self, message, errno):
            super(self.__class__, self).__init__(message)
            self.errno = errno

    def __init__(self, lib_path=None):
        lib = cdll.LoadLibrary(lib_path if lib_path else ctypes.util.find_library('sensors'))
        lib.sensors_init(None)

        self.sensors_get_adapter_name = log_wrapper(lib.sensors_get_adapter_name, c_char_p)
        self.sensors_get_all_subfeatures = log_wrapper(lib.sensors_get_all_subfeatures, POINTER(SensorsSubFeature))
        self.sensors_get_detected_chips = log_wrapper(lib.sensors_get_detected_chips, POINTER(ChipName))
        self.sensors_get_features = log_wrapper(lib.sensors_get_features, POINTER(SensorsFeature))
        self.sensors_get_label = log_wrapper(lib.sensors_get_label, c_char_p)
        self.sensors_get_value = log_wrapper(lib.sensors_get_value, c_int)
        self.sensors_snprintf_chip_name = log_wrapper(lib.sensors_snprintf_chip_name, c_int)
        self.sensors_strerror = log_wrapper(lib.sensors_strerror, c_char_p)

        self.sensors_get_value.errcheck = self._errcheck
        self.sensors_snprintf_chip_name.errcheck = self._errcheck

    def _errcheck(self, result, func, arguments):
        if result < 0:
            raise self.ParseError(bytes(self.sensors_strerror(result)).decode(), result)
        return result

    def _get_features(self, chip_p, response, i):
        while True:
            feature_p = self.sensors_get_features(chip_p, byref(i))

            if feature_p:
                feature_data = feature_p.contents.to_python(self)
                logging.debug(feature_data)

                feature_data.update(sub_features=self._get_sub_features(chip_p, feature_p, {}, c_int()))

                label_p = self.sensors_get_label(chip_p, feature_p)
                if label_p:
                    feature_data['label'] = bytes(string_at(label_p)).decode()
                    logging.debug(feature_data['label'])
                else:
                    logging.debug('* No label')

                response[feature_data['name']] = feature_data
            else:
                logging.debug('Done iter sensors_get_features')
                return response

    def _get_sub_features(self, chip_p, feature_p, response, i):
        while True:
            sub_feature_p = self.sensors_get_all_subfeatures(chip_p, feature_p, byref(i))

            if sub_feature_p:
                sub_feature = sub_feature_p.contents
                sub_feature_data = sub_feature.to_python(self)
                logging.debug(sub_feature_data)

                value = c_double()
                self.sensors_get_value(chip_p, sub_feature.number, byref(value))
                logging.debug(value.value)

                sub_feature_data.update(value=value.value)
                response[sub_feature_data['name']] = sub_feature_data
            else:
                logging.debug('Done iter sensors_get_all_subfeatures')
                return response

    def _get_chip_name(self, chip_p):
        result = create_string_buffer(1024)
        self.sensors_snprintf_chip_name(result, len(result), chip_p)

        return bytes(result.value).decode()

    def get_data(self):
        response = {}
        i = c_int()

        while True:
            chip_p = self.sensors_get_detected_chips(0, byref(i))

            if chip_p:
                chip_data = chip_p.contents.to_python(self)
                logging.debug(chip_data)

                name = self._get_chip_name(chip_p)
                logging.debug(name)

                chip_data.update(name=name, features=self._get_features(chip_p, {}, c_int()))
                response[chip_data['prefix']] = chip_data
            else:
                logging.debug('Done iter sensors_get_detected_chips')
                return response

    def get_cpu_temp(self, data=None, sensor='coretemp'):
        data = data if data else self.get_data()

        for key in (sensor, 'coretemp', 'acpitz'):
            try:
                return data[key]['features']['temp1']['sub_features']['temp1_input']['value']
            except KeyError:
                continue

        raise self.Error('Temperature sensor driver not found')
