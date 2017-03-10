import os

from skywiserestclient import SkyWiseResource, SkyWiseJSON


class ModelApiResource(SkyWiseJSON, SkyWiseResource):
    pass

_site = os.getenv('SKYWISE_MODEL_SITE', 'https://model.api.wdtinc.com')
_user = os.getenv('SKYWISE_MODEL_APP_ID', '')
_password = os.getenv('SKYWISE_MODEL_APP_KEY', '')

ModelApiResource.set_site(_site)
ModelApiResource.set_user(_user)
ModelApiResource.set_password(_password)


def map_async(skywise_requests, raise_on_error=True):
    return ModelApiResource.map(skywise_requests, raise_on_error=raise_on_error)


from .model import Model
from .forecast import Forecast
