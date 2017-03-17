from functools import partial

from jsonschema import Draft4Validator

from .errors import ValidationError


def load(schema, validator, request):
    validator.check_schema(schema)
    v = validator(schema)
    errors = sorted(v.iter_errors(request.json), key=lambda e: e.path)
    if errors:
        raise ValidationError(errors)

    return request.json


def loader(schema, validator=Draft4Validator):
    """Create a load function based on schema dict and IValidator class.

    :param schema: The schema to validate with.
    :param validator: The IValidator class that will be used to validate
        the instance. Default to ``Draft4Validator``.

    You can plug this ``load`` function into a json view.

    Returns a ``load`` function that takes a request JSON body
    and uses the schema to validate it. This function raises
    :class:`jsonschema.ValidationError` if validation is not successful.
    """
    return partial(load, schema, validator)
