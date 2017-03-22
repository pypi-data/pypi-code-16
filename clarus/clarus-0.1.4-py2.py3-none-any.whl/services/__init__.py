import clarus
import clarus.api
from clarus.models import ApiResponse, ApiError

__all__ = [u'compliance', u'frtb', u'hedge', u'margin', u'market', u'portfolio', u'profitloss', u'risk', u'sdr', u'simm', u'trade', u'upload', u'util', u'xva']

def api_request(serviceCategory, service, output=None, **params):
    httpresp = clarus.api.request(serviceCategory, service, output, **params);
    if (httpresp.status_code != 200):
        raise ApiError(httpresp)
    else:
        return ApiResponse(httpresp);
