# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Implements all of the security mechanisms in use by the providers."""


import inspect


ALWAYS = 0b1111     # ALWAYS is the default scope and the initialization value


class ScopeError(Exception):
    """An exception for invalid scopes."""

    def __init__(self, message, function):
        """Initialize the exception."""
        _file = inspect.getfile(function)
        _, _line = inspect.getsourcelines(function)

        err_msg = '%s (File "%s", line %s)'
        super().__init__(err_msg % (message, _file, _line))


def checkpoint(scope=ALWAYS, priority=10, methods=None):
    """Decorate a provider method to make it a security checkpoint.

    A security checkpoint is a method of a provider executed each time the
    latter is required to process a request, to verify if prerequisites are
    met. If those prerequisites aren't met, the security checkpoint has the
    responsability to gracefully terminate the request with a call to abort().

    Each variable parts of an URL is passed as keyword argument to the
    decorated method. The unexpected keyword arguments are simply ignored.

    A security checkpoint possesses three attributes : scope, priority and
    methods. The scope is the combination of one or more values to determine
    when the security checkpoint should be executed. The valid values are a
    named propagation rule of the provider or the following flags:

    - Provider.ALWAYS:
      The security checkpoint is always executed. (default value)

    - Provider.IS_DEST:
      The security checkpoint is executed each time a propagation rule of the
      provider is executed.

    - Provider.IS_ENTRY:
      The security checkpoint is executed each time the provider is the one
      selected by the application as the entry-point for the processing.

    - Provider.IS_NOT_DEST:
      The negation of Provider.IS_DEST.

    - Provider.IS_NOT_ENTRY:
      The negation of Provider.IS_ENTRY.

    Each flag is cumulative with the help of '&' logical operator. Beware,
    some flags are incompatible and could raise an exception !

    The priority determines the execution order of each security checkpoint in
    the current scope. A lower number is an higher priority level. The default
    level is set to 10.

    The methods is used to limit the security checkpoint to certain HTTP verbs.
    It accepts the name of one verb or a tuple for more of them. The default
    value is None and is used to disable the limitation to certain HTTP verbs.

    Usages:

            @checkpoint
            def default_checkpoint(self, id):
                ...

            @checkpoint(scope=Provider.IS_ENTRY & Provider.IS_DEST)
            def single_scope_checkpoint(self, name=None):
                ...

            @checkpoint(scope=(Provider.IS_ENTRY, 'propagation_rule'))
            def multiple_scope_checkpoint(self, **kwargs):
                ...

            @checkpoint(priority=1, methods='GET')
            def high_priority_get_checkpoint(self):
                ...
    """
    if hasattr(scope, '__call__'):  # the decorator is used with default values
        func = scope
        setattr(func, '__is_checkpoint', ((ALWAYS,), priority, methods))
        return func

    if methods is not None and not isinstance(methods, tuple):
        methods = methods,

    if not isinstance(scope, tuple):
        scope = scope,

    def decorator(func):

        for desc in scope:
            if not isinstance(desc, int):
                continue

            if desc == ALWAYS and len(scope) > 1:
                raise ScopeError('ALWAYS is masking other scopes.', func)

            if not (desc % 4 and desc >> 2):
                raise ScopeError('Conflicting scope detected.', func)

        setattr(func, '__is_checkpoint', (scope, priority, methods))
        return func

    return decorator
