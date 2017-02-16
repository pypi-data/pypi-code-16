from typing import Any, List

from .utils import JSON_PRIMITIVES


def validate(value: Any, spec: type) -> bool:
    """Test whether a value is valid.

    Arguments:
      value: The value to validate.
      spec: The specification to validate it against.

    Returns:
      :py:class:`bool`: Whether the ``value`` matches the ``spec``.

    """
    if value is None:
        return True
    if isinstance(value, list) and issubclass(spec, List):
        return True
    if isinstance(value, spec):
        return True
    if isinstance(value, dict):
        if spec in JSON_PRIMITIVES or spec is list:
            return False
        if issubclass(spec, List):
            return False
        return True
    return False
