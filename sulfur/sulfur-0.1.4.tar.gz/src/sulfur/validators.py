from html5lib import HTMLParser
from html5lib.html5parser import ParseError

from sulfur.errors import ValidationError
from sulfur.simplehtml5 import SimpleHtml5Validator


class Html5Validator:
    """
    Validates HTML5 data using a series of methods.
    """

    @classmethod
    def as_validator(cls, name):
        """
        Return a validator function from the given validator method name.
        """

        try:
            getattr(cls, name + '_validator')
        except AttributeError:
            raise ValueError('invalid validator: %r' % name)

        def validator(data):
            instance = cls(data)
            method = getattr(instance, name + '_validator')
            return method()

        return validator

    def __init__(self, data):
        self.data = data

    def default_validator(self):
        """
        Default validation method.

        Just check if tags are well formed and if all tags that should close,
        indeed close.
        """

        validator = SimpleHtml5Validator(self.data)
        validator.validate()

    def strict_validator(self):
        """
        Strict validation method.

        We just call html5lib parser with strict=True. Error messages are awful,
        and it complaints about many small errors, so it can be annoying.
        """

        strict_parser = HTMLParser(strict=True)
        try:
            strict_parser.parse(self.data)
        except ParseError as ex:
            raise ValidationError(str(ex))