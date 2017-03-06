from dict_validator import Field


class BooleanField(Field):
    """
    Match a boolean.

    >>> from dict_validator import validate, describe

    >>> class Schema:
    ...     field = BooleanField()

    >>> list(validate(Schema, {"field": True}))
    []

    >>> list(validate(Schema, {"field": 11}))
    [(['field'], 'Not a boolean')]

    >>> list(describe(Schema))
    [([], {'type': 'Dict'}), (['field'], {'type': 'Boolean'})]

    """

    @property
    def _type(self):
        return "Boolean"

    def _validate(self, value):
        if not isinstance(value, bool):
            return "Not a boolean"
