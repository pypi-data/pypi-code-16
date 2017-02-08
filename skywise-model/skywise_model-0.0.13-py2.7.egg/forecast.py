from voluptuous import Any, Schema
from . import ModelApiResource
from ._validation import datetime, datetime_to_str
from ._variable import Variable

STATUS_INITIALIZING = 'INITIALIZING'
STATUS_INCOMPLETE = 'INCOMPLETE'
STATUS_COMPLETE = 'COMPLETE'
STATUS_EXPIRED = 'EXPIRED'

_forecast_deserialize = Schema({
    'id': Any(None, str, unicode),
    'model': Any(str, unicode),
    'createTime': datetime,
    'initTime': datetime,
    'variables': Any(str, unicode),
    'status': Any(str, unicode),
    'model_id': Any(str, unicode),
    'expirationTime': datetime
})

_forecast_serialize = Schema({
    'id': Any(None, str, unicode),
    'model_id': Any(str, unicode),
    'initTime': datetime_to_str,
    'status': Any(str, unicode),
    'expirationTime': datetime_to_str
})


class _ForecastMixin(object):

    def get_variables(self, **kwargs):
        return Variable.find(forecast_id=self.id, **kwargs)

    def add_variable(self, platform_product_id, platform_forecast_id):
        variable = Variable()
        variable.forecast_id = self.id
        variable.platform_forecast_product_id = platform_product_id
        variable.platform_forecast_id = platform_forecast_id
        variable.save()
        return variable


class Forecast(ModelApiResource, _ForecastMixin):

    _path = '/models/{model_id}/forecasts'

    _args = Schema({
        'start': datetime_to_str,
        'end': datetime_to_str,
        'initTime': datetime_to_str,
        'limit': int,
        'sort': Any('asc', 'desc'),
        'status': Any(str, unicode)
    })

    _deserialize = _forecast_deserialize

    _serialize = _forecast_serialize

    @classmethod
    def find(cls, id_=None, **kwargs):
        if id_ is not None:
            return _ForecastById.find(id_)
        return super(Forecast, cls).find(**kwargs)

    def save(self, **kwargs):
        if self.id:
            forecast = _ForecastById()
            forecast._data = self._data
            forecast.save(**kwargs)
            return forecast.id
        return super(Forecast, self).save(**kwargs)


class _ForecastById(ModelApiResource, _ForecastMixin):

    _path = '/forecasts'

    _deserialize = _forecast_deserialize

    _serialize = _forecast_serialize
