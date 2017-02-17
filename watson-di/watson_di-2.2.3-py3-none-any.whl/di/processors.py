# -*- coding: utf-8 -*-
import abc
from inspect import isfunction, signature
from types import FunctionType
from watson import di
from watson.common.contextmanagers import suppress
from watson.di.types import FUNCTION_TYPE


class Base(di.ContainerAware, metaclass=abc.ABCMeta):

    """The base processor that all other processors should extend.

    When a processor is called from the container the following parameters are
    sent through with the event.

        - definition: The dict definition of the dependency
        - dependency: The name of the dependency

    Depending on the event, a different target will also be sent with the event.

        - watson.di.container.PRE_EVENT: The dict definition of the dependency
        - watson.di.container.POST_EVENT: The initialized dependency
    """
    @abc.abstractmethod
    def __call__(self, event):
        raise NotImplementedError(
            'The processor <{}> must implement __call__'.format(get_qualified_name(self)))  # pragma: no cover

    def get_args_kwargs(self, obj):
        args, kwargs = [], {}
        if isinstance(obj, dict):
            for key, val in obj.items():
                kwargs[key] = get_param_from_container(val, self.container)
        elif isinstance(obj, list):
            for arg in obj:
                args.append(get_param_from_container(arg, self.container))
        return args, kwargs


class ConstructorInjection(Base):

    """Responsible for initializing the dependency.

    Responsible for initializing the dependency and injecting any required
    values into the constructor.

    Args:
        event (watson.events.types.Event): The event dispatched from the container.

    Returns:
        mixed: The dependency
    """

    def instantiate(self, definition):
        item = definition['item']
        if hasattr(item, '__ioc_definition__'):
            definition.update(item.__ioc_definition__)
        args, kwargs = [], {}
        is_lambda = definition.get('call_type', None) == FUNCTION_TYPE
        sig = signature(item)
        if 'container' in sig.parameters:
            kwargs['container'] = self.container
        if 'init' in definition:
            init = definition['init']
            updated_args, updated_kwargs = self.get_args_kwargs(init)
            args.extend(updated_args)
            kwargs.update(updated_kwargs)
            if isfunction(init):
                sig = signature(init)
                if 'container' in sig.parameters:
                    kwargs['container'] = self.container
                init = init(*args, **kwargs)
                definition['init'] = init
            if not is_lambda:
                args, kwargs = self.get_args_kwargs(init)
        item = item(*args, **kwargs)
        if is_lambda and isinstance(item, str):
            # Special case for items that might be retrieved via lambda expressions
            with suppress(Exception):
                definition['item'] = self.container.load_item_from_string(item)
                item, args, kwargs = self.instantiate(definition)
        return item, args, kwargs

    def __call__(self, event):
        definition = event.params['definition']
        item, args, kwargs = self.instantiate(definition)
        return item


class SetterInjection(Base):

    """Responsible for injecting required values into setter methods.

    Args:
        event (watson.events.types.Event): The event dispatched from the container.

    Returns:
        mixed: The dependency
    """

    def __call__(self, event):
        item = event.target
        definition = event.params['definition']
        if 'setter' in definition:
            for setter, args in definition['setter'].items():
                method = getattr(item, setter)
                if isinstance(args, dict):
                    kwargs = {arg: get_param_from_container(
                              value,
                              self.container) for arg,
                              value in args.items()}
                    method(**kwargs)
                elif isinstance(args, list):
                    args = [get_param_from_container(arg, self.container)
                            for arg in args]
                    method(*args)
                else:
                    method(get_param_from_container(args, self.container))
        return item


class AttributeInjection(Base):

    """Responsible for injecting required values into attributes.

    Args:
        event (watson.events.types.Event): The event dispatched from the
                                           container.

    Returns:
        mixed: The dependency
    """

    def __call__(self, event):
        item = event.target
        if 'property' in event.params['definition']:
            for prop, value in event.params['definition']['property'].items():
                setattr(
                    item,
                    prop,
                    get_param_from_container(
                        value,
                        self.container))
        return item


class ContainerAware(Base):

    """Injects the container into a dependency.

    Responsible for injecting the container in any class that extends
    watson.di.ContainerAware. The container is then accessible via object.container

    Args:
        event (watson.events.types.Event): The event dispatched from the container.

    Returns:
        mixed: The dependency
    """

    def __call__(self, event):
        item = event.target
        if isinstance(item, di.ContainerAware):
            item.container = self.container
        return item


def get_param_from_container(param, container):
    """Internal function used by the container.

    Retrieve a parameter from the container, and determine whether or not that
    parameter is an existing dependency.

    Returns:
        mixed: The dependency (if param name is the same as a dependency), the
               param, or the value of the param.
    """
    if param in container.params:
        param = container.params[param]
        if param in container:
            param = container.get(param)
    elif param in container:
        param = container.get(param)
    else:
        if isinstance(param, FunctionType):
            param = param(container)
    return param
