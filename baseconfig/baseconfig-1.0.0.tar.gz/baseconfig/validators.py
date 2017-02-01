import baseconfig


class Validator():
    def __init__(self, is_valid):
        self._is_valid = is_valid

    @property
    def is_valid(self):
        return self._is_valid

    def ensure_valid(self, value):
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                "The value %s was rejected by the validator." % (value,))


class LengthValidator(Validator):
    def __init__(self, expected_length):
        super().__init__(lambda x: len(x) == expected_length)
        self._expected_length = expected_length

    def ensure_valid(self, value):
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                "The length of value {value} is {actual}. The expected length "
                "is {expected}.".format(
                    value=value,
                    actual=len(value),
                    expected=self._expected_length))


class MaxLengthValidator(Validator):
    def __init__(self, max_length):
        super().__init__(lambda x: len(x) <= max_length)
        self._max_length = max_length

    def ensure_valid(self, value):
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                "The length of value {value} is {actual}. The maximum allowed "
                "length is {expected}.".format(
                    value=value,
                    actual=len(value),
                    expected=self._max_length))


class OneOfValidator(Validator):
    def __init__(self, *allowed):
        super().__init__(lambda x: x in allowed)
        self._allowed = allowed

    def ensure_valid(self, value):
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                "The value {value} is not among the allowed values "
                "{allowed}.".format(value=value, allowed=self._allowed))


class RangeValidator(Validator):
    def __init__(self, inclusive_min, inclusive_max):
        super().__init__(lambda x: x >= inclusive_min and x <= inclusive_max)
        self._min = inclusive_min
        self._max = inclusive_max

    def ensure_valid(self, value):
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                "The value {value} is outside the range {min}..{max}.".format(
                    value=value, min=self._min, max=self._max))


class OfTypeValidator(Validator):
    def __init__(self, of_type):
        super().__init__(lambda x: isinstance(x, of_type))
        self._of_type = of_type

    def ensure_valid(self, value):
        if not self._is_valid(value):
            actual = type(value).__name__
            expected = self._of_type.__name__

            if actual == expected:
                actual = type(value)
                expected = self._of_type

            raise baseconfig.InvalidValueException(
                "The value {value} of type {actual} is not of type "
                "{expected}.".format(
                    value=value, actual=actual, expected=expected))
