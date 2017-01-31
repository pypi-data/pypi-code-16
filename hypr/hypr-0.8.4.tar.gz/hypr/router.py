# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Request router."""


import re
import asyncio

from aiohttp.web import Response
from aiohttp.abc import AbstractRouter, AbstractMatchInfo
from hypr.globals import LocalStorage
from hypr.converters import DEFAULT_CONVERTERS
from hypr.serializers import choose_media_type
from hypr.web_exceptions import HTTPTemporaryRedirect, HTTPMethodNotAllowed, \
    HTTPNotFound, HTTPNotAcceptable


# regex to match the different segments of an URL rule
_rule_re = re.compile(r'''
    (?P<static>[^<]*)                           # static rule data
    <
    (?:
        (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name
        (?:\((?P<args>.*?)\))?                  # converter arguments
        \:                                      # variable delimiter
    )?
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
    >
''', re.VERBOSE)

# regex to match converter arguments
_converter_args_re = re.compile(r'''
    ((?P<name>\w+)\s*=\s*)?
    (?P<value>
        True|False|
        -?(\d+.)?\d+(e[-+]\d+)?|
        -?\d+.|
        \w+|
        [urUR]?(?P<stringval>"[^"]*?"|'[^']*')|
    )\s*,
''', re.VERBOSE | re.UNICODE)

# translation table text -> python constants
_PYTHON_CONSTANTS = {
    'None':     None,
    'True':     True,
    'False':    False
}


def _pythonize(value):
    if value in _PYTHON_CONSTANTS:
        return _PYTHON_CONSTANTS[value]
    for convert in int, float:
        try:
            return convert(value)
        except ValueError:
            pass
    if value[:1] == value[-1:] and value[0] in '"\'':
        value = value[1:-1]
    return str(value)


def get_converter(converter_name, args, kwargs):
    """Look up the converter for the given parameter."""
    if converter_name not in DEFAULT_CONVERTERS:
        raise LookupError('The converter %s does not exist' % converter_name)
    return DEFAULT_CONVERTERS[converter_name](*args, **kwargs)


def parse_rule(rule):
    """Parse an URL rule.

    Parse a rule and return it as a generator. Each iteration yields tuples
    in the form ``(converter, arguments, variable)``. If the converter is
    `None` it's static url part, otherwise it's a dynamic one.
    """
    pos = 0
    end = len(rule)

    do_match = _rule_re.match
    used_names = set()

    while pos < end:
        match = do_match(rule, pos)
        if match is None:
            break

        # yield static segment
        data = match.groupdict()
        if data['static']:
            yield None, None, data['static']

        # yield variable segment
        variable = data['variable']
        converter = data['converter'] or 'default'
        if variable in used_names:
            raise ValueError('variable name %r used twice.' % variable)
        used_names.add(variable)
        yield converter, data['args'] or None, variable

        pos = match.end()

    if pos < end:
        remaining = rule[pos:]
        if '>' in remaining or '<' in remaining:
            raise ValueError('malformed url rule: %r' % rule)
        yield None, None, remaining


def parse_converter_args(argstr):
    """Parse the arguments of a converter."""
    argstr += ','
    args = []
    kwargs = {}

    for item in _converter_args_re.finditer(argstr):
        value = item.group('stringval')
        if value is None:
            value = item.group('value')
        value = _pythonize(value)
        if not item.group('name'):
            args.append(value)
        else:
            name = item.group('name')
            kwargs[name] = value

    return tuple(args), kwargs


class Rule:
    """The Rule object associates an URL rule to a endpoint.

    The URL rule is then used to match the submitted URL of incoming requests
    and determine the valid endpoint to handle them. An URL rule defines a set
    of static and parameterized segments.

    The rule object also stores additional informations, such as the accepted
    methods to accelerate checks.
    """

    def __init__(self, url, endpoint, methods=None):
        """Init the Rule.

        Args:
            url (str): an URL rule.
            endpoint: the endpoint associated to the rule.
            methods: tuple of the accepted methods. (None for any)
        """
        self.url = url
        self.endpoint = endpoint

        self.methods = None
        if methods is not None:
            self.methods = set([m.upper() for m in methods])

        self.arguments = set()
        self.is_leaf = not url.endswith('/')
        self._trace = self._converters = self._regex = self._weight = None

    def compile(self):
        """Compile the URL rule to a regular expression and store it."""
        self._trace = []
        self._weights = []
        self._converters = {}

        regex_parts = []

        def _build_regex(rule):

            for converter, arguments, variable in parse_rule(rule):
                if converter is None:
                    regex_parts.append(re.escape(variable))
                    self._trace.append((False, variable))
                    for part in variable.split('/'):
                        if part:
                            self._weights.append((0, -len(part)))
                else:
                    if arguments:
                        c_args, c_kwargs = parse_converter_args(arguments)
                    else:
                        c_args = ()
                        c_kwargs = {}
                    convobj = get_converter(converter, c_args, c_kwargs)
                    regex_parts.append('(?P<%s>%s)' % (variable,
                                                       convobj.regex))
                    self._converters[variable] = convobj
                    self._trace.append((True, variable))
                    self._weights.append((1, convobj.weight))
                    self.arguments.add(str(variable))

        _build_regex(self.is_leaf and self.url or self.url.rstrip('/'))
        if not self.is_leaf:
            self._trace.append((False, '/'))

        regex = r'^{}{}$'.format(
            ''.join(regex_parts),
            not self.is_leaf and '(?<!/)(?P<__suffix__>/?)' or ''
        )

        self._regex = re.compile(regex, re.UNICODE)

    def match(self, path):
        """Check if the rule matches a given path.

        If the rule matches a dict with the converted values is returned,
        otherwise the return value is `None`.
        """
        m = self._regex.search(path)
        if m is not None:
            groups = m.groupdict()

            if not self.is_leaf and not groups.pop('__suffix__'):
                raise HTTPTemporaryRedirect(path + '/')

            result = {}
            for name, value in groups.items():
                try:
                    value = self._converters[name].to_python(value)
                except ValueError:
                    return
                result[str(name)] = value

            return result

    def match_compare_key(self):
        """The match compare key for sorting.

        Current implementation:
        1.  rules without any arguments come first for performance
            reasons only as we expect them to match faster and some
            common ones usually don't have any arguments (index pages etc.)
        2.  The more complex rules come first so the second argument is the
            negative length of the number of weights.
        3.  lastly we order by the actual weights.
        """
        return bool(self.arguments), -len(self._weights), self._weights


class MatchInfo(dict, AbstractMatchInfo):
    """Matching informations of a Rule."""

    def __init__(self, match_dict, rule, provider, serializer, mimetype):
        """Init MatchInfo."""
        super().__init__(match_dict)
        self._provider = provider
        self._rule = rule
        self._serializer = serializer
        self._mimetype = mimetype
        self._apps = []
        self._frozen = False

    @property
    def apps(self):
        return tuple(self._apps)

    def add_app(self, app):
        if self._frozen:
            raise RuntimeError("Cannot change apps stack after .freeze() call")
        self._apps.insert(0, app)

    @property
    def endpoint(self):
        """Return the endpoint."""
        return self._rule.endpoint

    @property
    def handler(self):
        """Request handler."""
        def ensure_response(request):

            if self._serializer is None:
                raise HTTPNotAcceptable()

            rv = yield from self._provider.local_dispatcher(self, request.method)

            status_or_headers = headers = None
            if isinstance(rv, tuple):
                rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))

            if isinstance(status_or_headers, (list, dict)):
                headers, status_or_headers = status_or_headers, None

            if not isinstance(rv, Response):

                data = rv
                rv = Response(headers=headers, status=status_or_headers or 200)
                rv.headers['content-type'] = self._mimetype     # set mimetype
                rv.text = self._serializer(data, request)
                headers = status_or_headers = None

            return rv

        return ensure_response

    def __repr__(self):     # pragma: no cover
        """Representation of the MatchInfo object."""
        return "<MatchInfo {}: {}>".format(super().__repr__(), self._rule)


class Router(AbstractRouter):
    """Hypr router."""

    def __init__(self, app):
        super().__init__()
        self._app = app
        self._rules = []
        self._providers = {}
        self._serializers = {}

    def _propagate(self):
        for provider in self._providers.values():
            provider.__class__._propagate()

    @asyncio.coroutine
    def resolve(self, request, path=None, method=None):
        """Return the match_info for the given request."""
        # determine the best mimetype/serializer for the response
        mimetype = None
        serializer = None

        if request is not None:
            path = request.path
            method = request.method
            app = self._app

            accept = request.headers.get('accept', '*/*')
            mimetype = choose_media_type(accept, app.available_mimetypes)
            serializer = self._serializers.get(mimetype)

            LocalStorage().set('request', request)

        allowed_methods = set()

        for rule in self._rules:
            # search the matching rule
            match_dict = rule.match(path)
            if match_dict is None:
                continue

            # get the provider if the rule handles the HTTP method
            if rule.methods is None or method in rule.methods:
                provider = self._providers[rule.endpoint]
                return MatchInfo(match_dict, rule, provider,
                                 serializer, mimetype)

            allowed_methods.update(rule.methods)

        if allowed_methods:
            raise HTTPMethodNotAllowed(method, allowed_methods)
        else:
            raise HTTPNotFound()

    def set_serializers(self, serializers):
        """Set the available serializers."""
        self._serializers = serializers

    def add_provider(self, provider, *urls, methods=None, endpoint=None,
                     propagation=False):
        """Register a provider with URL rules.

        Args:
            provider: a Provider class.
            *urls: one or more path to access the provider.
            methods: a tuple containing the allowed HTTP methods.
                If methods is none, the allowed methods are determined from
                the provider implementation.
            endpoint: the name of the endpoint. If endpoint is none, the name
                is the provider's name.
        """
        provider._attach_to(self._app)

        if endpoint is None:
            endpoint = provider.__name__    # default endpoint

        if methods is None:
            methods = provider.methods

        if endpoint in self._providers:
            err_msg = 'endpoint %s is already in use'
            raise RuntimeError(err_msg % endpoint)

        path = None
        for path in urls:

            if not path.startswith('/'):
                err_msg = 'url \'%s\' should start with a leading \'/\''
                raise RuntimeError(err_msg % path)

            rule = Rule(path, endpoint, methods)
            rule.compile()
            self._rules.append(rule)
            self._rules.sort(key=lambda x: x.match_compare_key())

        if path:
            self._providers[endpoint] = provider()

        # register propagation
        if propagation:
            endpoint = '__pps_%s' % endpoint
            urls = tuple(
                ('%s' % ('/', '')[url[-1] == '/']).join((url, '<path:__pps>'))
                for url in urls if '<path:' not in url
            )

            if urls:
                self.add_provider(provider, *urls, endpoint=endpoint)

    def get_provider(self, endpoint):

        rv = self._providers.get(endpoint)
        if rv is not None:
            return rv.__class__
        return None

    def iter_rules(self, endpoint=None):

        return (rule.url for rule in self._rules if endpoint is None or
                rule.endpoint == endpoint)
