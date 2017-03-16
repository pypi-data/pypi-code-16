import datetime
from congo.conf import settings
from congo.maintenance import get_domain

def set_cookie(response, key, value, days_expire = None, domain = None):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60 # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds = max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

    kwargs = {
        'key': key,
        'value': value,
        'max_age': max_age,
        'expires': expires,
        'secure': settings.SESSION_COOKIE_SECURE or None,
    }

    if domain:
        kwargs['domain'] = domain

    response.set_cookie(**kwargs)

def del_cookie(response, value):
    response.set_cookie(value, '', expires = 0)

def get_cookie(request, value, default = None):
    if value in request.COOKIES:
        return request.COOKIES[value]
    else:
        return default
