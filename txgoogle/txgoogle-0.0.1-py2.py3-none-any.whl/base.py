def BOOL(val):
    return 'true' if val else 'false'


def INT(val):
    return str(int(val))


def ONEOF(*values):
    def proxy(val):
        if not val in values:
            raise ValueError('%s not in %s' % (val, ','.join(values)))
        return val
    return proxy


def SET(*set_values):
    set_values = set(set_values)
    def proxy(val):
        if isinstance(val, basestring):
            val = set(val.split(','))
        else:
            val = set(val)
        if set_values.issuperset(val):
            return ','.join(val)
        else:
            raise ValueError('%s not in %s' % (val, set_values))
    return proxy


class GoogleApi(object):
    _url = None
    _apis = {}

    def __init__(self, parent):
        self._parent = parent

    def request(self, url, method, query=None, body=None):
        return self._parent.request(self._url + url, method, query, body)

    def __getattr__(self, item):
        if not item in self._apis:
            raise AttributeError('No such API (%s)' % item)
        api = self._apis[item](self)
        setattr(self, item, api)
        return api


class GoogleApiEndPoint(object):
    _url = None

    _methods = {}

    def __init__(self, parent):
        self._parent = parent

        for method, decl in self._methods.items():
            setattr(self, method, self._make_method(decl))

    def request(self, method='GET', query=None, body=None):
        return self._parent.request(self._url, method, query, body)

    def _make_method(self, decl):
        def proxy(**kwargs):
            body = kwargs.get('body')

            query = {}
            if 'required' in decl:
                for arg_name, arg_decl in decl['required'].items():
                    query[arg_name] = arg_decl(kwargs[arg_name])

            if 'filter' in decl:
                filter_count = 0
                for arg_name, arg_decl in decl['filter'].items():
                    val = kwargs.get(arg_name)
                    if val is not None:
                        query[arg_name] = arg_decl(val)
                        filter_count += 1
                if filter_count != 1:
                    raise RuntimeError('must specify exactly one of %s' % ', '.join(decl['filter']))

            if 'optional' in decl:
                for arg_name, arg_decl in decl['optional'].items():
                    val = kwargs.get(arg_name)
                    if val is not None:
                        query[arg_name] = arg_decl(val)

            return self.request(decl['method'], query, body)

        return proxy
