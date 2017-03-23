from __future__ import print_function, unicode_literals
import clarus
import clarus.api
from clarus.models import ApiResponse, ApiError

__all__ = ['compliance', 'frtb', 'hedge', 'margin', 'market', 'portfolio', 'profitloss', 'risk', 'sdr', 'simm', 'trade', 'upload', 'util', 'xva']

def api_request(serviceCategory, service, output=None, **params):
    httpresp = clarus.api.request(serviceCategory, service, output, **params);
    if (httpresp.status_code != 200):
        raise ApiError(httpresp)
    else:
        return ApiResponse(httpresp);
