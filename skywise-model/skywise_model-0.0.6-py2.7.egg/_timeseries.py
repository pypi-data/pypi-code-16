from voluptuous import Any, Schema
from . import ModelApiResource
from ._validation import datetime, datetime_to_str


class TimeSeries(ModelApiResource):

    _path = '/variables/{variable_id}/timeseries/{lat}/{lon}'

    _deserialize = Schema({
        'series': [{
            'validTime': datetime,
            'value': float
        }],
        'maximum': {
            'validTime': datetime,
            'value': float
        },
        'minimum': {
            'validTime': datetime,
            'value': float
        },
        'mean': float,
        'median': float,
        'mode': float,
        'unit': {
            'description': Any(str, unicode),
            'label': Any(str, unicode)
        }
    })

    _serialize = Schema({
        'series': [{
            'validTime': datetime_to_str,
            'value': float
        }],
        'maximum': {
            'validTime': datetime_to_str,
            'value': float
        },
        'minimum': {
            'validTime': datetime_to_str,
            'value': float
        },
        'mean': float,
        'median': float,
        'mode': float,
        'unit': {
            'description': Any(str, unicode),
            'label': Any(str, unicode)
        }
    })
