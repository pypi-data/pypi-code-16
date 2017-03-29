from voluptuous import Any, Schema
from . import ModelApiResource
from ._validation import datetime, datetime_to_str


class TimeSeries(ModelApiResource):

    _path = '/variables/{variable_id}/timeseries/{lat}/{lon}'

    _deserialize = Schema({
        'series': [{
            'validTime': datetime,
            'value': Any(None, float)
        }],
        'maximum': {
            'validTime': datetime,
            'value': Any(None, float)
        },
        'minimum': {
            'validTime': datetime,
            'value': Any(None, float)
        },
        'mean': Any(None, float),
        'median': Any(None, float),
        'mode': Any(None, float),
        'unit': {
            'description': Any(str, unicode),
            'label': Any(str, unicode)
        }
    })

    _serialize = Schema({
        'series': [{
            'validTime': datetime_to_str,
            'value': Any(None, float)
        }],
        'maximum': {
            'validTime': datetime_to_str,
            'value': Any(None, float)
        },
        'minimum': {
            'validTime': datetime_to_str,
            'value': Any(None, float)
        },
        'mean': Any(None, float),
        'median': Any(None, float),
        'mode': Any(None, float),
        'unit': {
            'description': Any(str, unicode),
            'label': Any(str, unicode)
        }
    })
