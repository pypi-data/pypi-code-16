from voluptuous import Any, Schema
from . import ModelApiResource
from ._validation import datetime, datetime_to_str
from ._timeseries import TimeSeries


class Variable(ModelApiResource):

    _path = '/forecasts/{forecast_id}/variables'

    _deserialize = Schema({
        "id": Any(str, unicode),
        "name": Any(str, unicode),
        "description": Any(str, unicode),
        "validTimes": [datetime],
        "forecast": Any(str, unicode),
        'forecast_id': Any(str, unicode),
        'model_platform_forecast_product_id': Any(str, unicode),
        'platform_forecast_id': Any(str, unicode)
    })

    _serialize = Schema({
        "id": Any(None, str, unicode),
        "name": Any(str, unicode),
        "description": Any(str, unicode),
        "validTimes": [datetime_to_str],
        "forecast": Any(str, unicode),
        'forecast_id': Any(str, unicode),
        'model_platform_forecast_product_id': Any(str, unicode),
        'platform_forecast_product_id': Any(str, unicode),
        'platform_forecast_id': Any(str, unicode)
    })

    def get_timeseries(self, lat, lon):
        return TimeSeries.find(variable_id=self.id, lat=lat, lon=lon)

    def get_timeseries_async(self, lat, lon):
        ts = TimeSeries.find_async(variable_id=self.id, lat=lat, lon=lon)
        ts.tag(variable=self)
        return ts
