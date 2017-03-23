import json
from six import string_types

from globus_cli.helpers import outformat_is_json
from globus_cli.safeio.write import safeprint


class PrintableErrorField(object):
    """
    A glorified tuple with a kwarg in its constructor
    """
    TEXT_PREFIX = 'Globus CLI Error:'

    def __init__(self, name, value, multiline=False):
        self.name = name
        self.value = value
        self.multiline = multiline

    @property
    def _text_prefix_len(self):
        return len(self.TEXT_PREFIX)

    def __str__(self):
        """
        str(PrintableErrorField) is good for textmode printing
        """
        name = self.name + ':'
        if not self.multiline or not isinstance(self.value, string_types) or \
                '\n' not in self.value:
            return '{0} {1}'.format(name.ljust(self._text_prefix_len),
                                    self.value)
        else:
            spacer = '\n' + ' '*(self._text_prefix_len + 1)
            return '{0}{1}{2}'.format(
                name, spacer, spacer.join(self.value.split('\n')))


def write_error_info(error_name, fields):
    message = None
    if outformat_is_json():
        # dictify joined tuple lists and dump to json string
        message = json.dumps(
            dict(
                [('error_name', error_name)] +
                [(f.name, f.value) for f in fields]),
            indent=2)
    else:
        message = 'A {0} Occurred.\n{1}'.format(
            error_name, '\n'.join(str(f) for f in fields))
        message = '{0} {1}'.format(PrintableErrorField.TEXT_PREFIX, message)

    safeprint(message, write_to_stderr=True)
