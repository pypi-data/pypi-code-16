from requests import HTTPError
from voluptuous import Any, Schema

from . import ModelApiResource
from .exc import (ModelAlreadyExistsException, ModelNotFound,
                  ModelPlatformForecastProductAlreadyExists)
from .forecast import Forecast, LatestForecast
from ._subscription import Subscription


class Model(ModelApiResource):

    _path = '/models'

    _deserialize = Schema({
        'id': Any(str, unicode),
        'name': Any(str, unicode),
        'description': Any(str, unicode),
        'forecasts': Any(str, unicode)
    })

    _serialize = Schema({
        'id': Any(None, str, unicode),
        'name': Any(str, unicode),
        'description': Any(str, unicode),
        'forecasts': Any(str, unicode)
    })

    @classmethod
    def find(cls, id_=None, **kwargs):
        if not id_:
            return super(Model, cls).find(**kwargs)

        try:
            return super(Model, cls).find(id_)
        except HTTPError as e:
            if "model_does_not_exist" in e.response.content:
                raise ModelNotFound()
            raise e

    def save(self, **kwargs):
        try:
            super(Model, self).save(**kwargs)
        except HTTPError as e:
            if "model_already_exists" in e.response.content:
               raise ModelAlreadyExistsException()
            raise e

    def latest_forecast(self):
        return LatestForecast.find(model_id=self.id)

    def get_forecasts(self, **kwargs):
        forecasts = Forecast.find(model_id=self.id, **kwargs)
        for forecast in forecasts:
            forecast.model = self
        return forecasts

    def get_forecast_by_id(self, forecast_id):
        forecast = Forecast.find(forecast_id)
        forecast.model = self
        return forecast

    def create_forecast(self, init_time):
        forecast = Forecast()
        forecast.initTime = init_time
        forecast.model_id = self.id
        forecast.save()
        forecast.model = self
        return forecast

    def get_platform_forecast_products(self, **kwargs):
        return _ModelPlatformForecastProduct.find(model_id=self.id, **kwargs)

    def add_platform_forecast_product(self, name, description, platform_forecast_product_id):
        p = _ModelPlatformForecastProduct()
        p.name = name
        p.description = description
        p.platform_forecast_product_id = platform_forecast_product_id
        p.model_id = self.id

        try:
            p.save()
        except HTTPError as e:
            if 'mpfp_already_exists' in e.response.content:
                raise ModelPlatformForecastProductAlreadyExists()
        return p

    def subscribe(self, event, subscriber_email, options=None):
        subscription = Subscription()
        subscription.model_id = self.id
        subscription.event = event
        subscription.subscriber_email = subscriber_email
        if options is None:
            options = {}
        subscription.options = options
        subscription.save()
        return subscription

    def get_subscriptions(self, **kwargs):
        return Subscription.find(model_id=self.id, **kwargs)


class _ModelPlatformForecastProduct(ModelApiResource):

    _path = '/models/{model_id}/platform-forecast-products'

    _deserialize = Schema({
        'id': Any(str, unicode),
        'name': Any(str, unicode),
        'description': Any(str, unicode),
        'model_id': Any(str, unicode),
        'platform_forecast_product_id': Any(str, unicode)
    })

    _serialize = Schema({
        'name': Any(str, unicode),
        'description': Any(str, unicode),
        'model_id': Any(str, unicode),
        'platform_forecast_product_id': Any(str, unicode)
    })

    def save(self, **kwargs):
        super(_ModelPlatformForecastProduct, self).save(model_id=self.model_id, **kwargs)
