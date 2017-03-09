from __future__ import print_function


def get_input(msg, default=None):
    prompt = '{msg}{default}: '.format(
        msg=msg,
        default=('' if default is None else ' ({})'.format(default))
    )
    try:
        input = raw_input  # p2
    except NameError:
        pass  # py3
    return input(prompt) or default


def console(msg):
    print(msg)


def log(message, **defaults):
    def wrap(func):
        def wrapped(*args, **kwargs):
            params = {}

            import inspect
            spec = inspect.getargspec(func)

            for i, v in enumerate(spec.args or ()):
                params[v] = args[i] if i < len(args) else kwargs.get(v, None)

            if 'self' in params:
                attrs = {k: v for k, v in params.pop('self').__dict__.items() if k[0].isalpha() and not callable(v)}
                params = dict(attrs, **params)

            for k, v in defaults.items():
                if not params.get(k, None):
                    params[k] = v

            console(message.format(**params))
            result = func(*args, **kwargs)

            return result

        return wrapped

    return wrap


def current_ip():
    try:
        from urllib2 import urlopen  # py2
    except ImportError:
        from urllib.request import urlopen  # py3
    return urlopen('http://ip.42.pl/raw').read()


def cidr(ip, length=32):
    return ip + ('/{}'.format(length) if '/' not in ip else '')


class RequireError(Exception):
    pass


def require(msg=None, **parameters):
    invalid = {}
    for key, value in parameters.items():
        if not value:
            invalid[key] = value
    if invalid:
        if msg:
            console(msg)
        else:
            console('Parameters: `{}` are required.'.format(', '.join(invalid.keys())))

        raise RequireError()
