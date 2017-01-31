# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Implements the base provider."""


import asyncio
import inspect

from hypr.router import Router
from collections import defaultdict


# frozenset of the allowed HTTP methods
HTTP_METHODS = frozenset(['get', 'post', 'head', 'options', 'delete', 'put',
                          'trace', 'patch'])


def _sort(checkpoints):
    # checkpoints is a dictionary where key is the function name of the CP
    # and the value is a tuple (priority, methods). The CP are sorted by
    # proprity, then a list of tuples name, methods is returned.
    checkpoints = sorted(checkpoints.items(), key=lambda x: x[1][0])
    return tuple((name, methods) for name, (_, methods) in checkpoints)


class _ProviderType(type):
    # Perform some class initialization like detecting available HTTP methods
    # and setting up the internal router.

    def __new__(mcs, name, bases, d):

        cls = type.__new__(mcs, name, bases, d)

        methods = set()
        checkpoints = defaultdict(dict)

        # get all the name of propagation rules in the current provider
        rules = ()
        if cls.propagation is not None:
            rules = tuple(name for name in cls.propagation.keys()
                          if not name.startswith('__pps_'))

        for name, func in inspect.getmembers(cls, inspect.isfunction):

            if name in HTTP_METHODS:
                methods.add(name.upper())

            # get the scope and settings of checkpoints
            scope, *settings = getattr(func, '__is_checkpoint', ((),))
            for element in scope:
                # the checkpoint is executed when the rule is applied
                if not isinstance(element, int):
                    checkpoints['__src_%s' % element][name] = settings
                    checkpoints['__lnk_%s' % element][name] = settings
                    continue

                if element & 0b1010 == 0b1010:
                    checkpoints['__sngl'][name] = settings

                if element & 0b0101 == 0b0101:
                    for rule in rules:
                        checkpoints['__lnk_%s' % rule][name] = settings

                if element & 0b1001 == 0b1001:
                    for rule in rules:
                        checkpoints['__src_%s' % rule][name] = settings

                if element & 0b0110 == 0b0110:
                    checkpoints['__dest'][name] = settings

        # flatten and sort checkpoints = cp[scope] = [(func, methods), ...]
        cls._checkpoints = {s: _sort(cp) for s, cp in checkpoints.items()}

        cls.methods = cls.methods or tuple(methods)
        cls._router = Router(None)

        return cls


class Provider(metaclass=_ProviderType):
    """Base class of all providers.

    The provider has the responsibility to dispatch a request to the rightful
    method in order to get the response. The methods able to provide a response
    are named after the HTTP methods (see HTTP_METHODS).

    Propagation
    -----------

    The provider is able to delegate the request processing to another provider
    with the help of a propagation mechanism. The propagation allows to
    register a path to another provider relative to this one.

    Three methods are available to declare a propagation.

    * Declarative method :

    The declarative method is the preferred one as it allows to perform static
    analysis of it. To declare a propagation, each provider class possesses a
    `propagation` attribute where it is possible to list rules. The attribute
    is a dict, a rule is a key-value pair where the key is the endpoint of the
    propagation rule and the value is a tuple with the target provider as the
    first element of it, and URL rules are the subsequent elements.

        class SourceProvider(Provider):

            propagation = {
                'rule0' : (TargetProvider, '/target'),
                'rule1' : OtherProvider
            }

            ...

    If no URL rules are specified, the propagation rule uses the URLs rules
    associated at the app-level with registered target provider. The tuple
    notation is not mandatory for this latter use case. All the propagation
    rules set with the declarative method are resolved at the application
    startup.

    * Imperative method :

    The imperative method allows to declare a propagation rule at the runtime.

        SourceProvider.add_propagation(TargetProvider, '/target')

    This method is potentially harmful and must be used with caution.

    * Decorative method :

    The decorative method is a class decorator for the provider to declare
    a propagation. Optional arguments allow to specify various settings. The
    mechanism of the decorator is based on the declarative method and does not
    require specific usage cautions.

        @SourceProvider.propagate
        class TargetProvider(Provider):

            ...

    Both of declarative and imperative methods support the use of app-level
    registered endpoints instead of providers as target for the propagation.

    Security
    --------

    The security of the provider is achieved with the help of methods
    considered as security checkpoints. To mark a method as a security
    checkpoint the decorator @checkpoint must be used:

        @checkpoint
        def security_checkpoint(self):
            ...

    The decorated method is called by the provider before continuing with
    further tasks and is responsible, with the help of abort(), to stop the
    request processing if the wanted conditions are not met. The decorated
    method accepts arguments the same way as any other HTTP method.

    Each security checkpoint possesses attributes to set when to call it (see
    checkpoint() documentation for mor informations).
    """

    # The checkpoint's scope is encoded on 4 bits and is set with these flags :

    ALWAYS = 0b1111         # always run the checkpoint (CP)

    IS_DEST = 0b1110        # run the CP if the provider is the destination.
    IS_NOT_DEST = 0b1101    # run the CP if there is a propagation.
    IS_ENTRY = 0b1011       # run the CP if the provider is the entry point.
    IS_NOT_ENTRY = 0b0111   # run the CP if the provider is not entry point.

    # A recurring flag setting :
    IS_LINK = 0b0101        # the provider is nor the entry, nor the dest.

    propagation = None
    _sentinel = False

    methods = None

    @classmethod
    def _attach_to(cls, app):
        cls._router._app = app

    @classmethod
    def _propagate(cls):
        # recursive method called to registed all declared propagation rules.
        # this method is not intended to be used by the user.
        if cls.propagation is not None and not cls._sentinel:
            for endpoint, rule in cls.propagation.items():
                if not isinstance(rule, tuple):
                    rule = rule,

                provider, *urls = rule
                cls.add_propagation(provider, *urls, endpoint=endpoint)\
                   ._propagate()
            cls._sentinel = True    # recursion failsafe

    @classmethod
    def add_propagation(cls, provider, *urls, methods=None, endpoint=None):
        """Add a propagation rule.

        Args:
            provider: a provider class or an app-level endpoint.
            *urls: URL rules to access the target provider.
                If none is provided the propagation rule will fall back into
                app-level registered rules.
            methods: a tuple containing the allowed HTTP methods.
                If methods is none, the allowed methods are determined from
                the provider implementation.
            endpoint: the propagation endpoint.
                If the endpoint is none, the provider's name is used.

        Returns:
            The target provider.
        """
        app = cls._router._app

        if app is None:
            raise RuntimeError('%s is not reachable.' % cls.__name__)

        # convert string to provider
        target = None
        if not isinstance(provider, _ProviderType):
            target = provider
            provider = app.router.get_provider(provider)

        if provider is None:
            err_msg = '%s -> %s : unknown provider.'
            raise RuntimeError(err_msg % (cls.__name__, target))

        if target is None:
            target = provider.__name__

        if not urls:
            urls = tuple(app.router.iter_rules(target))

        if not urls:
            err_msg = '%s -> %s : explicit URLs required'
            raise RuntimeError(err_msg % (cls.__name__, provider.__name__))

        if endpoint is None:
            endpoint = provider.__name__
        # ensure the user is not messing with automatic endpoints
        endpoint = endpoint.replace('__', '_%s__' % cls.__name__)

        if methods is None:
            methods = provider.methods

        # register main URLs
        cls._router.add_provider(provider, *urls, methods=methods,
                                 endpoint=endpoint, propagation=True)

        return provider

    @classmethod
    def propagate(cls, *urls, methods=None, endpoint=None):
        """A class decorator used to declare a propagation rule.

        This does the same thing as add_propagation() but is intended for
        decorator usage. If no argument is submitted, the app-level URL rules
        of the decorated provider are used:

            @Provider0.propagate
            class Provider1(Provider):
                ...

            @Provider0.propagate('/custom-url')
            class Provider2(Provider):
                ...

        The @propagate decorator uses the same arguments as add_propagation().
        """
        def decorator(provider, _urls=None):
            if _urls is None:
                _urls = urls

            _endpoint = endpoint or provider.__name__

            if cls.propagation is None:
                cls.propagation = {}

            if endpoint in cls.propagation:
                err_msg = '%s : endpoint %s is already in use'
                raise RuntimeError(err_msg % (cls.__name__, _endpoint))

            cls.propagation[_endpoint] = (provider,) + _urls
            return provider

        if urls and isinstance(urls[0], _ProviderType):
            return decorator(urls[0], urls[1:])

        return decorator

    @asyncio.coroutine
    def _call_meth(self, match_info, name):
        # call meth with variable segments of the request as arguments.
        meth = getattr(self, name)
        if (not asyncio.iscoroutinefunction(meth) and
                not inspect.isgeneratorfunction(meth)):
            meth = asyncio.coroutine(meth)

        # get variable segments for the current provider.
        var = {k: v for k, v in match_info.items() if not k.startswith('_')}

        # get method signature and apply variable segments
        req, _, kw, _ = inspect.getargspec(getattr(meth, '__wrapped__', meth))
        if kw is None:
            rv = yield from meth(**{k: v for k, v in var.items() if k in req})
        else:
            rv = yield from meth(**var)  # any kerword arguments is accepted
        return rv

    @asyncio.coroutine
    def _execute_checkpoints(self, strategy, verb, match_info):
        # execute all the checkpoints of the selected strategy
        checkpoints = self._checkpoints.get(strategy, ())
        for name, verbs in checkpoints:
            if verbs is None or verb in verbs:
                yield from self._call_meth(match_info, name)

    @asyncio.coroutine
    def local_dispatcher(self, match_info, method, entry=True):
        """Dispatch the request for processing."""
        path = match_info.get('__pps')
        if path is not None:
            path = '/%s' % path     # add required leading /
            target = yield from self._router.resolve(None, path, method)

            # get the applied rule (remove __pps_ prefix if necessary)
            endpoint = target.endpoint
            if endpoint.startswith('__pps_'):
                endpoint = endpoint[6:]

            # select the checkpoint strategy from entry
            strategy = '__%s_%s' % (('lnk', 'src')[entry], endpoint)

            yield from self._execute_checkpoints(strategy, method, match_info)
            rv = yield from target._provider.local_dispatcher(target, method,
                                                              False)
            return rv

        if entry:
            yield from self._execute_checkpoints('__sngl', method, match_info)
        else:
            yield from self._execute_checkpoints('__dest', method, match_info)

        rv = yield from self._call_meth(match_info, method.lower())
        return rv
