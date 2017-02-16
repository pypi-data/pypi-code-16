from typing import Any, Callable, List

from .validation import validate
from .utils import JSON_PRIMITIVES, memoize


class Wrapper:

    __annotations__ = {}

    def __init__(self, json: dict):
        self._json = json

    def __getattribute__(self, item: str) -> Any:
        if item in ('_json', '__annotations__'):
            return super().__getattribute__(item)
        value = self._json.get(item)
        if value is not None:
            spec = self.__annotations__.get(item)
            return _convert(value, spec)
        return super().__getattribute__(item)


def build_converter(method: Callable) -> Callable:
    return_type = method.__annotations__.get('return')
    if return_type is None:
        return _simple_convert
    if return_type in JSON_PRIMITIVES:
        return return_type
    return _get_converter(return_type)


def _convert(value, spec):
    if spec is not None:
        if not validate(value, spec):
            raise TypeError(
                '{!r} does not meet specification {!r}'.format(value, spec)
            )
        return _get_converter(spec)(value)
    return _simple_convert(value)


def _get_converter(spec):
    return (_array_factory if issubclass(spec, List) else _object_factory)(spec)


def _simple_convert(value):
    if isinstance(value, dict):
        return Wrapper(value)
    elif isinstance(value, list):
        return [_simple_convert(element) for element in value]
    return value


@memoize
def _object_factory(spec):
    combined_dict = dict(**Wrapper.__dict__)
    combined_dict.update(**spec.__dict__)
    return type(spec.__name__, (spec, Wrapper), combined_dict)


@memoize
def _array_factory(spec):
    type_args = getattr(spec, '__args__', None)
    if type_args is None:
        converter = _simple_convert
    else:
        converter = _get_converter(type_args[0])

    def array_factory(values: list) -> list:
        return [converter(value) for value in values]

    return array_factory
